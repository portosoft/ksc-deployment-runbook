# -*- coding: utf-8 -*-
"""Testes dos passos reais de instalação (R-01, desmockagem de setup_steps).

Todos os comandos de sistema são interceptados: nenhum teste altera o host.
"""

import logging
import os
import stat
from pathlib import Path

import pytest

from automation.python import setup_steps
from automation.python.setup_steps import (
    SetupError,
    build_response_file,
    configure_web_console,
    ensure_os_prereqs,
    install_ksc_server,
    post_install_hardening,
    setup_postgres,
)


@pytest.fixture
def logger():
    log = logging.getLogger("test.setup_steps")
    log.addHandler(logging.NullHandler())
    return log


@pytest.fixture
def recorded(monkeypatch):
    """Intercepta run_command e registra as invocações."""
    calls = []

    def fake_run_command(cmd, check=True, capture_output=True, env=None, input_data=None):
        calls.append({"cmd": cmd, "input": input_data})
        return ("", "", 0)

    monkeypatch.setattr(setup_steps, "run_command", fake_run_command)
    return calls


def _cmds(calls):
    return [" ".join(c["cmd"]) for c in calls]


# --- Pré-requisitos do SO ---------------------------------------------------


def test_os_prereqs_installs_on_supported_os(monkeypatch, recorded, logger, ksc_test_config):
    monkeypatch.setattr(
        setup_steps, "_read_os_release", lambda: {"ID": "rocky", "VERSION_ID": "9.4"}
    )
    ensure_os_prereqs(ksc_test_config, logger)

    assert any(c.startswith("dnf install -y tar") for c in _cmds(recorded))


def test_os_prereqs_refuses_unsupported_os(monkeypatch, recorded, logger, ksc_test_config):
    monkeypatch.setattr(
        setup_steps, "_read_os_release", lambda: {"ID": "ubuntu", "VERSION_ID": "24.04"}
    )
    with pytest.raises(SetupError, match="fora do escopo"):
        ensure_os_prereqs(ksc_test_config, logger)

    assert recorded == [], "nenhum comando pode rodar em SO não suportado"


def test_dry_run_executes_nothing(monkeypatch, recorded, logger, ksc_test_config):
    monkeypatch.setattr(
        setup_steps, "_read_os_release", lambda: {"ID": "rocky", "VERSION_ID": "9.4"}
    )
    ensure_os_prereqs(ksc_test_config, logger, dry_run=True)

    assert recorded == []


# --- PostgreSQL -------------------------------------------------------------


def test_postgres_skips_provisioning_when_remote(recorded, logger, ksc_test_config):
    remote = ksc_test_config.model_copy(update={"db_host": "db.interno.test"})
    setup_postgres(remote, logger)

    assert recorded == [], "banco remoto não deve ser provisionado localmente"


def test_postgres_skips_initdb_when_cluster_exists(monkeypatch, recorded, logger, ksc_test_config):
    monkeypatch.setattr(Path, "exists", lambda self: True)
    setup_postgres(ksc_test_config, logger)

    assert not any("initdb" in c for c in _cmds(recorded))
    assert any("systemctl enable --now postgresql-16" == c for c in _cmds(recorded))


def test_postgres_password_never_reaches_argv(monkeypatch, recorded, logger, ksc_test_config):
    monkeypatch.setattr(Path, "exists", lambda self: True)
    setup_postgres(ksc_test_config, logger)

    for call in recorded:
        assert ksc_test_config.db_password not in " ".join(call["cmd"])

    role_calls = [c for c in recorded if c["input"] and "CREATE ROLE" in c["input"]]
    assert len(role_calls) == 1
    assert ksc_test_config.db_password in role_calls[0]["input"]


def test_postgres_creates_both_databases(monkeypatch, recorded, logger, ksc_test_config):
    monkeypatch.setattr(Path, "exists", lambda self: True)
    setup_postgres(ksc_test_config, logger)

    sql = " ".join(c["input"] or "" for c in recorded)
    assert 'CREATE DATABASE "ksc"' in sql
    assert f'CREATE DATABASE "{ksc_test_config.db_name}"' in sql


# --- Arquivo de respostas ---------------------------------------------------


def test_response_file_uses_config_values(ksc_test_config):
    content = build_response_file(ksc_test_config)

    assert f"KLSRV_UNATT_DBMS_INSTANCE={ksc_test_config.db_host}" in content
    assert f"KLSRV_UNATT_DBMS_PORT={ksc_test_config.db_port}" in content
    assert f"KLSRV_UNATT_SERVERADDRESS={ksc_test_config.ksc_fqdn}" in content
    assert "EULA_ACCEPTED=1" in content


def test_response_file_written_with_mode_0600(tmp_path, monkeypatch, ksc_test_config):
    monkeypatch.chdir(tmp_path)
    path = setup_steps._write_response_file(build_response_file(ksc_test_config))
    try:
        mode = stat.S_IMODE(os.stat(path).st_mode)
        assert mode == 0o600
    finally:
        os.remove(path)


# --- Instalação do KSC ------------------------------------------------------


def _stage_rpms(directory):
    for name in (
        "ksc64-16.3.0-1207.x86_64.rpm",
        "klnagent64-16.3.0-1207.x86_64.rpm",
        "ksc-web-console-16.3.12907.x86_64.rpm",
    ):
        (directory / name).write_bytes(b"")


def test_install_requires_packages_dir(recorded, logger, ksc_test_config, monkeypatch):
    monkeypatch.delenv("KSC_PACKAGES_DIR", raising=False)
    config = ksc_test_config.model_copy(update={"packages_dir": None})
    with pytest.raises(SetupError, match="KSC_PACKAGES_DIR"):
        install_ksc_server(config, logger)


def test_install_fails_when_rpm_missing(tmp_path, monkeypatch, recorded, logger, ksc_test_config):
    monkeypatch.setattr(setup_steps, "verify_ksc_packages", lambda *a, **k: None)
    config = ksc_test_config.model_copy(update={"packages_dir": str(tmp_path)})

    with pytest.raises(SetupError, match="não encontrado"):
        install_ksc_server(config, logger)


def test_install_rejects_duplicate_versions(tmp_path, monkeypatch, recorded, logger, ksc_test_config):
    monkeypatch.setattr(setup_steps, "verify_ksc_packages", lambda *a, **k: None)
    _stage_rpms(tmp_path)
    (tmp_path / "ksc64-16.2.0-1023.x86_64.rpm").write_bytes(b"")
    config = ksc_test_config.model_copy(update={"packages_dir": str(tmp_path)})

    with pytest.raises(SetupError, match="Mais de um pacote"):
        install_ksc_server(config, logger)


def test_install_runs_postinstall_and_removes_answers(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    monkeypatch.setattr(setup_steps, "verify_ksc_packages", lambda *a, **k: None)
    _stage_rpms(tmp_path)
    config = ksc_test_config.model_copy(update={"packages_dir": str(tmp_path)})

    written = {}
    original = setup_steps._write_response_file

    def spy(content):
        path = original(content)
        written["path"] = path
        return path

    monkeypatch.setattr(setup_steps, "_write_response_file", spy)
    monkeypatch.setattr(setup_steps, "_ksc_is_configured", lambda: False)
    install_ksc_server(config, logger)

    cmds = _cmds(recorded)
    assert any(c.startswith("dnf install -y") and "ksc64-" in c for c in cmds)
    assert any(setup_steps.KSC_POSTINSTALL in c for c in cmds)
    assert not os.path.exists(written["path"]), "arquivo de respostas deve ser removido"


def test_answers_removed_even_when_postinstall_fails(
    tmp_path, monkeypatch, logger, ksc_test_config
):
    monkeypatch.setattr(setup_steps, "verify_ksc_packages", lambda *a, **k: None)
    _stage_rpms(tmp_path)
    config = ksc_test_config.model_copy(update={"packages_dir": str(tmp_path)})

    def failing(cmd, check=True, capture_output=True, env=None, input_data=None):
        if any(setup_steps.KSC_POSTINSTALL in part for part in cmd):
            return ("", "erro crítico no postinstall", 1)
        return ("", "", 0)

    monkeypatch.setattr(setup_steps, "run_command", failing)
    monkeypatch.setattr(setup_steps, "_ksc_is_configured", lambda: False)
    monkeypatch.setattr(setup_steps, "_ensure_ksc_accounts", lambda *a, **k: None)

    written = {}
    original = setup_steps._write_response_file
    monkeypatch.setattr(
        setup_steps,
        "_write_response_file",
        lambda content: written.setdefault("path", original(content)),
    )

    with pytest.raises(SetupError, match="postinstall.pl falhou"):
        install_ksc_server(config, logger)

    assert not os.path.exists(written["path"])


# --- Hardening --------------------------------------------------------------


def test_hardening_writes_ld_library_path_dropin(tmp_path, monkeypatch, recorded, logger, ksc_test_config):
    dropin_dir = tmp_path / "kladminserver_srv.service.d"
    monkeypatch.setattr(setup_steps, "SYSTEMD_DROPIN_DIR", str(dropin_dir))
    monkeypatch.setattr(setup_steps, "KSC_SERVICES", [])

    post_install_hardening(ksc_test_config, logger)

    content = (dropin_dir / setup_steps.SYSTEMD_DROPIN_NAME).read_text()
    assert f"Environment=LD_LIBRARY_PATH={setup_steps.KSC_LIB_DIR}" in content
    assert any("daemon-reload" in c for c in _cmds(recorded))


def test_hardening_fails_when_services_inactive(tmp_path, monkeypatch, recorded, logger, ksc_test_config):
    monkeypatch.setattr(setup_steps, "SYSTEMD_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "_unit_is_active", lambda unit: False)

    with pytest.raises(SetupError, match="não ficaram ativos"):
        post_install_hardening(ksc_test_config, logger)


def test_dry_run_without_packages_dir_warns_instead_of_failing(
    monkeypatch, recorded, logger, ksc_test_config
):
    """Em --check, a ausência dos pacotes é condição de ambiente, não erro fatal."""
    monkeypatch.delenv("KSC_PACKAGES_DIR", raising=False)
    config = ksc_test_config.model_copy(update={"packages_dir": None})

    install_ksc_server(config, logger, dry_run=True)

    assert recorded == []


def test_apply_without_packages_dir_still_fails(monkeypatch, recorded, logger, ksc_test_config):
    """O gate permanece fatal fora da simulação."""
    monkeypatch.delenv("KSC_PACKAGES_DIR", raising=False)
    config = ksc_test_config.model_copy(update={"packages_dir": None})

    with pytest.raises(SetupError, match="KSC_PACKAGES_DIR"):
        install_ksc_server(config, logger, dry_run=False)


def test_os_prereqs_are_valid_on_el9():
    """libidn (v1) não existe no EL9 e abortava a instalação; o pacote é libidn2."""
    assert "libidn" not in setup_steps.OS_PREREQ_PACKAGES
    assert "libidn2" in setup_steps.OS_PREREQ_PACKAGES
    # perl é exigido pelo postinstall.pl, que é o instalador silencioso do KSC.
    assert "perl" in setup_steps.OS_PREREQ_PACKAGES


def test_accounts_created_before_installer(monkeypatch, recorded, logger):
    """O postinstall.pl aborta se o grupo administrativo não existir previamente."""
    monkeypatch.setattr(setup_steps, "_account_exists", lambda kind, name: False)
    setup_steps._ensure_ksc_accounts(logger)

    cmds = _cmds(recorded)
    assert any(c.startswith(f"groupadd --system {setup_steps.KSC_ADMINS_GROUP}") for c in cmds)
    assert any("useradd" in c and setup_steps.KSC_SERVICE_USER in c for c in cmds)


def test_existing_accounts_are_preserved(monkeypatch, recorded, logger):
    """Conta já no grupo correto não é tocada."""
    monkeypatch.setattr(setup_steps, "_account_exists", lambda kind, name: True)

    def fake(cmd, check=True, capture_output=True, env=None, input_data=None):
        recorded.append({"cmd": cmd, "input": input_data})
        return (f"{setup_steps.KSC_ADMINS_GROUP} outro", "", 0)

    monkeypatch.setattr(setup_steps, "run_command", fake)
    setup_steps._ensure_ksc_accounts(logger)

    assert not any(
        c["cmd"][0] in ("useradd", "groupadd", "usermod") for c in recorded
    ), "contas existentes e já no grupo não devem ser alteradas"


def test_existing_account_outside_group_is_added(monkeypatch, recorded, logger):
    """Conta preexistente fora de kladmins seria trancada para fora pelo hardening.

    O hardening fecha o acesso de "outros" e concede apenas ao grupo: uma conta
    de serviço fora dele perde acesso aos próprios binários (203/EXEC).
    """
    monkeypatch.setattr(setup_steps, "_account_exists", lambda kind, name: True)

    def fake(cmd, check=True, capture_output=True, env=None, input_data=None):
        recorded.append({"cmd": cmd, "input": input_data})
        return ("outrogrupo", "", 0)

    monkeypatch.setattr(setup_steps, "run_command", fake)
    setup_steps._ensure_ksc_accounts(logger)

    assert any(
        c["cmd"][:2] == ["usermod", "-aG"] for c in recorded
    ), "a conta precisa ser adicionada ao grupo administrativo"


def test_response_file_matches_account_constants(ksc_test_config):
    """As contas criadas e as declaradas no arquivo de respostas têm de coincidir."""
    content = build_response_file(ksc_test_config)

    assert f"KLSRV_UNATT_KLADMINSGROUP={setup_steps.KSC_ADMINS_GROUP}" in content
    assert f"KLSRV_UNATT_KLSVCUSER={setup_steps.KSC_SERVICE_USER}" in content
    assert f"KLSRV_UNATT_KLSRVUSER={setup_steps.KSC_SERVICE_USER}" in content


def test_hardening_grants_group_access_before_removing_world_access(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    """chmod -R o-rwx isolado tirava do serviço a travessia de /opt/kaspersky.

    Os binários pertencem a root e o klserver roda como a conta de serviço, que
    dependia da permissão de "outros" — removê-la sem conceder acesso ao grupo
    fazia o serviço falhar com 203/EXEC.
    """
    monkeypatch.setattr(setup_steps, "SYSTEMD_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "KSC_SERVICES", [])

    post_install_hardening(ksc_test_config, logger)

    cmds = _cmds(recorded)
    chgrp_idx = next(i for i, c in enumerate(cmds) if c.startswith("chgrp"))
    chmod_idx = next(i for i, c in enumerate(cmds) if "o-rwx" in c and "/opt/kaspersky" in c)
    assert chgrp_idx < chmod_idx, "o grupo precisa ser ajustado antes de fechar 'outros'"
    assert "g+rX" in cmds[chmod_idx]


def test_web_console_is_not_treated_as_a_systemd_unit():
    """O RPM do Web Console não cria ksc-web-console.service."""
    assert "ksc-web-console.service" not in setup_steps.KSC_SERVICES
    assert "kladminserver_srv.service" in setup_steps.KSC_SERVICES


def test_postinstall_skipped_when_already_configured(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    """postinstall.pl recusa reexecução: 'Do not run the postinstall.pl script again'.

    Reexecutar setup --apply em um host já configurado não pode falhar.
    """
    monkeypatch.setattr(setup_steps, "verify_ksc_packages", lambda *a, **k: None)
    monkeypatch.setattr(setup_steps, "_ksc_is_configured", lambda: True)
    monkeypatch.setattr(setup_steps, "_account_exists", lambda kind, name: True)
    _stage_rpms(tmp_path)
    config = ksc_test_config.model_copy(update={"packages_dir": str(tmp_path)})

    install_ksc_server(config, logger)

    assert not any(setup_steps.KSC_POSTINSTALL in c for c in _cmds(recorded))


def test_hardening_restores_traversal_of_data_dir(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    """O diretório de dados é root:root; sem travessia o klserver não sobe."""
    monkeypatch.setattr(setup_steps, "SYSTEMD_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "KSC_SERVICES", [])

    post_install_hardening(ksc_test_config, logger)

    cmds = _cmds(recorded)
    assert f"chgrp {setup_steps.KSC_ADMINS_GROUP} {setup_steps.KSC_DATA_DIR}" in cmds
    assert f"chmod g+rx,o+rx {setup_steps.KSC_DATA_DIR}" in cmds
    # Nada é alterado recursivamente ali: contas de serviço do instalador, fora
    # do grupo administrativo, dependem das permissões que ele mesmo definiu.
    assert f"chgrp -R {setup_steps.KSC_ADMINS_GROUP} {setup_steps.KSC_DATA_DIR}" not in cmds


def test_failed_units_are_reset_before_enabling(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    monkeypatch.setattr(setup_steps, "SYSTEMD_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "_unit_is_active", lambda unit: True)

    post_install_hardening(ksc_test_config, logger)

    cmds = _cmds(recorded)
    for unit in setup_steps.KSC_SERVICES:
        reset = cmds.index(f"systemctl reset-failed {unit}")
        enable = cmds.index(f"systemctl enable --now {unit}")
        assert reset < enable


# --- Web Console ------------------------------------------------------------


def test_web_console_setup_uses_installer_key_names(ksc_test_config):
    """O setup.js lê defaultLangId/trusted/certPath; o exemplo histórico errava."""
    import json as _json

    data = _json.loads(setup_steps.build_web_console_setup(ksc_test_config))

    assert data["acceptEula"] is True
    assert data["address"] == ksc_test_config.ksc_fqdn
    assert data["port"] == ksc_test_config.web_port
    assert "defaultLangId" in data and "defaultLanguageId" not in data
    assert "trusted" in data and "trusted_cert" not in data


def test_web_console_grants_capability_for_privileged_port(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    """A unidade do instalador roda sem privilégio: sem a capacidade não há bind."""
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SETUP_FILE", str(tmp_path / "setup.json"))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SERVICES", [])

    configure_web_console(ksc_test_config.model_copy(update={"web_port": 443}), logger)

    dropin = tmp_path / "dropin.d" / setup_steps.WEB_CONSOLE_DROPIN_NAME
    assert "AmbientCapabilities=CAP_NET_BIND_SERVICE" in dropin.read_text()


def test_web_console_skips_capability_on_unprivileged_port(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SETUP_FILE", str(tmp_path / "setup.json"))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SERVICES", [])

    configure_web_console(ksc_test_config.model_copy(update={"web_port": 8080}), logger)

    assert not (tmp_path / "dropin.d").exists()


def test_web_console_setup_file_is_0600(tmp_path, monkeypatch, recorded, logger, ksc_test_config):
    target = tmp_path / "setup.json"
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SETUP_FILE", str(target))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SERVICES", [])

    configure_web_console(ksc_test_config.model_copy(update={"web_port": 8080}), logger)

    assert stat.S_IMODE(os.stat(target).st_mode) == 0o600


def test_data_dir_is_not_hardened_recursively(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    """chmod -R o-rwx no diretório de dados derrubava klserver e Web Console."""
    monkeypatch.setattr(setup_steps, "SYSTEMD_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "KSC_SERVICES", [])

    post_install_hardening(ksc_test_config, logger)

    cmds = _cmds(recorded)
    assert f"chmod -R o-rwx {setup_steps.KSC_DATA_DIR}" not in cmds
    assert f"chmod g+rx,o+rx {setup_steps.KSC_DATA_DIR}" in cmds


# --- Idempotência -----------------------------------------------------------


def test_precheck_skips_ports_when_ksc_already_installed(monkeypatch, logger, ksc_test_config):
    """A segunda execução de setup --apply abortava com as portas do próprio KSC.

    Em um host já instalado, 'porta 443 em uso' é o estado correto — tratá-la
    como falha crítica impedia a reexecução, e idempotência é requisito para
    uso em frota.
    """
    monkeypatch.setattr(setup_steps, "_ksc_is_configured", lambda: True)

    capturado = {}

    def fake_precheck(config, skip_ports=False):
        capturado["skip_ports"] = skip_ports
        from automation.python.checks import CheckResult

        return CheckResult(items=[])

    monkeypatch.setattr(setup_steps, "run_precheck", fake_precheck)
    setup_steps.perform_precheck_only(ksc_test_config, logger)

    assert capturado["skip_ports"] is True


def test_precheck_checks_ports_on_clean_host(monkeypatch, logger, ksc_test_config):
    monkeypatch.setattr(setup_steps, "_ksc_is_configured", lambda: False)

    capturado = {}

    def fake_precheck(config, skip_ports=False):
        capturado["skip_ports"] = skip_ports
        from automation.python.checks import CheckResult

        return CheckResult(items=[])

    monkeypatch.setattr(setup_steps, "run_precheck", fake_precheck)
    setup_steps.perform_precheck_only(ksc_test_config, logger)

    assert capturado["skip_ports"] is False


def test_web_console_setup_skipped_when_parameters_unchanged(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    """Reexecutar o setup.js regenera o certificado TLS e recria as contas.

    Em um Web Console já configurado com os mesmos parâmetros isso quebra a
    confiança de clientes que já aceitaram o certificado — e a auditoria não
    acusa a troca.
    """
    setup_file = tmp_path / "setup.json"
    setup_file.write_text(setup_steps.build_web_console_setup(ksc_test_config))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SETUP_FILE", str(setup_file))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SERVICES", [])
    monkeypatch.setattr(
        setup_steps,
        "run_command",
        lambda cmd, **kw: ("KSCWebConsole.service enabled", "", 0),
    )

    configure_web_console(ksc_test_config, logger)

    # Nenhuma chamada ao setup.js: o certificado existente é preservado.
    assert not any("setup.js" in " ".join(c["cmd"]) for c in recorded)


def test_web_console_reconfigured_when_parameters_differ(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    """Parâmetros diferentes são reconfiguração intencional: o setup.js roda."""
    setup_file = tmp_path / "setup.json"
    outra_porta = ksc_test_config.model_copy(update={"web_port": 8080})
    setup_file.write_text(setup_steps.build_web_console_setup(outra_porta))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SETUP_FILE", str(setup_file))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SERVICES", [])

    configure_web_console(ksc_test_config, logger)

    assert any("setup.js" in " ".join(c["cmd"]) for c in recorded)


def test_web_console_configured_when_unit_absent(
    tmp_path, monkeypatch, recorded, logger, ksc_test_config
):
    """Arquivo igual mas sem unidade significa instalação incompleta."""
    setup_file = tmp_path / "setup.json"
    setup_file.write_text(setup_steps.build_web_console_setup(ksc_test_config))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SETUP_FILE", str(setup_file))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_DROPIN_DIR", str(tmp_path / "dropin.d"))
    monkeypatch.setattr(setup_steps, "WEB_CONSOLE_SERVICES", [])

    configure_web_console(ksc_test_config, logger)

    assert any("setup.js" in " ".join(c["cmd"]) for c in recorded)


def test_group_check_failure_aborts_instead_of_assuming_ok(monkeypatch, recorded, logger):
    """Não ler os grupos não permite concluir que a conta está correta.

    Seguir em frente deixaria o hardening retirar-lhe o acesso aos binários.
    """
    monkeypatch.setattr(setup_steps, "_account_exists", lambda kind, name: True)
    monkeypatch.setattr(
        setup_steps, "run_command", lambda cmd, **kw: ("", "usuário desconhecido", 1)
    )

    with pytest.raises(SetupError, match="verificar os grupos"):
        setup_steps._ensure_ksc_accounts(logger)
