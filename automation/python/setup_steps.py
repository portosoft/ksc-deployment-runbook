# -*- coding: utf-8 -*-
"""
Passos de instalação do KSC 16.x.

Este módulo executa comandos **localmente no servidor alvo** (Rocky/Oracle
Linux 9) e assume que o processo roda como root ou sob sudo. Operações
remotas via SSH são responsabilidade de ``automation/ops/``.

Todos os passos aceitam ``dry_run``: nesse modo nenhum comando que altera o
sistema é executado, apenas registrado no log de evidências. É o que sustenta
o contrato ``--check`` da CLI.
"""

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import List, Optional

from .checks import CheckResult, _read_os_release, run_precheck
from .config import KscConfig
from .shell_utils import ShellCommandError, run_command

# Pré-requisitos de SO do KSC 16.x em RHEL 9 e derivados.
#
# Os RPMs do KSC não declaram dependências próprias (são autocontidos), então
# esta lista é mantida à mão. `perl` é exigido pelo postinstall.pl e
# `policycoreutils-python-utils` pelas operações de SELinux do hardening.
#
# Atenção ao EL9: o pacote é `libidn2`. O `libidn` v1 não existe no Rocky 9 e
# fazia a instalação abortar com "Unable to find a match: libidn".
OS_PREREQ_PACKAGES = [
    "tar",
    "curl",
    "wget",
    "perl",
    "libidn2",
    "policycoreutils-python-utils",
    # Bibliotecas de sistema do WeasyPrint, usadas por `kscctl audit --report`
    # para gerar o PDF de evidências. Sem elas a conversão falha na importação.
    "pango",
    "cairo",
    "gdk-pixbuf2",
]

# PostgreSQL 16 — conforme docs/05-instalacao-postgresql.md.
PGDG_REPO_RPM = (
    "https://download.postgresql.org/pub/repos/yum/reporpms/"
    "EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm"
)
PG_SETUP_BIN = "/usr/pgsql-16/bin/postgresql-16-setup"
PG_DATA_DIR = "/var/lib/pgsql/16/data"
PG_SERVICE = "postgresql-16"

# Caminhos e unidades do KSC.
KSC_ROOT = "/opt/kaspersky/ksc64"
KSC_LIB_DIR = f"{KSC_ROOT}/lib"
KSC_POSTINSTALL = f"{KSC_ROOT}/lib/bin/setup/postinstall.pl"
KSC_DATA_DIR = "/var/opt/kaspersky"
SYSTEMD_DROPIN_DIR = "/etc/systemd/system/kladminserver_srv.service.d"
SYSTEMD_DROPIN_NAME = "10-ld-library-path.conf"
# Unidades systemd criadas pelo instalador, verificadas em instalação real do
# KSC 16.3 em Rocky Linux 9. Não existe `ksc-web-console.service`: o RPM do Web
# Console instala arquivos, mas o serviço depende de configuração própria.
KSC_SERVICES = [
    "kladminserver_srv.service",
    "klnagent_srv.service",
    "kliam_srv.service",
    "klwebsrv_srv.service",
]

# Contas de sistema exigidas pelo instalador silencioso. O postinstall.pl NÃO
# as cria: se o grupo informado em KLSRV_UNATT_KLADMINSGROUP não existir, ele
# aborta com "But the kladmins group does not exist".
KSC_ADMINS_GROUP = "kladmins"
KSC_SERVICE_USER = "ksc"

# Web Console. O RPM instala os arquivos, mas quem configura o produto é o
# setup.js, executado pelo scriptlet de pós-instalação com o arquivo de
# parâmetros em /etc. As unidades não se chamam "ksc-web-console".
WEB_CONSOLE_DIR = "/var/opt/kaspersky/ksc-web-console"
WEB_CONSOLE_SETUP_FILE = "/etc/ksc-web-console-setup.json"
WEB_CONSOLE_SERVICES = [
    "KSCWebConsoleNATS.service",
    "KSCWebConsoleManagement.service",
    "KSCWebConsolePlugin.service",
    "KSCSvcWebConsole.service",
    "KSCWebConsole.service",
]
WEB_CONSOLE_DROPIN_DIR = "/etc/systemd/system/KSCWebConsole.service.d"
WEB_CONSOLE_DROPIN_NAME = "10-bind-privileged-port.conf"

# defaultLangId do instalador: 1046 = pt-BR, 1033 = en-US.
WEB_CONSOLE_LANG_ID = 1046

# Prefixos dos RPMs instalados pelo passo de instalação, em ordem de dependência.
KSC_RPM_PREFIXES = ["ksc64-", "klnagent64-", "ksc-web-console-"]

SUPPORTED_OS_IDS = {"rocky", "ol", "rhel", "almalinux", "centos"}


class SetupError(Exception):
    pass


def _run(
    cmd: List[str],
    logger: logging.Logger,
    dry_run: bool = False,
    check: bool = True,
    input_data: Optional[str] = None,
    redacted: bool = False,
) -> int:
    """Executa um comando do passo de instalação, registrando-o no log.

    Args:
        cmd: Comando e argumentos.
        logger: Logger da execução.
        dry_run: Se True, registra o comando e não o executa.
        check: Se True, código de retorno diferente de zero vira SetupError.
        input_data: Enviado ao stdin; use para dados sensíveis.
        redacted: Se True, o comando não é registrado na íntegra.

    Returns:
        Código de retorno do processo (0 em dry_run).

    Raises:
        SetupError: Se check=True e o comando falhar.
    """
    printable = "<comando com dados sensíveis omitido>" if redacted else " ".join(cmd)

    if dry_run:
        logger.info(f"[CHECK] Seria executado: {printable}")
        return 0

    logger.info(f"Executando: {printable}")
    try:
        stdout, stderr, rc = run_command(cmd, check=False, input_data=input_data)
    except Exception as e:
        raise SetupError(f"Falha ao invocar '{printable}': {e}")

    for line in (stdout or "").splitlines():
        logger.info(line.rstrip())

    if rc != 0:
        detail = (stderr or stdout or "").strip()
        if check:
            raise SetupError(f"Comando falhou (rc={rc}): {printable}. {detail}")
        logger.warning(f"Comando retornou rc={rc} (ignorado): {printable}. {detail}")

    return rc


def _set_selinux_mode(mode: str, logger: logging.Logger) -> None:
    """Configura o modo do SELinux via setenforce (0 ou 1)."""
    try:
        run_command(["setenforce", mode])
        logger.info(f"SELinux alterado para modo: {mode}")
    except ShellCommandError as e:
        logger.warning(
            f"Aviso: Falha ao tentar mudar SELinux para {mode}. Talvez não instalado? Erro: {e}"
        )


def _get_selinux_mode() -> str:
    """Obtém o modo atual do SELinux via getenforce."""
    try:
        stdout, _, rc = run_command(["getenforce"], check=False)
        if rc == 0:
            return stdout.strip().lower()
    except Exception:
        pass
    return "unknown"


def _unit_is_active(unit: str) -> bool:
    """Retorna True se a unidade systemd estiver ativa."""
    try:
        _, _, rc = run_command(["systemctl", "is-active", "--quiet", unit], check=False)
        return rc == 0
    except Exception:
        return False


def ensure_os_prereqs(
    config: KscConfig, logger: logging.Logger, dry_run: bool = False
) -> None:
    """Instala os pré-requisitos de SO exigidos pelo KSC 16.x.

    Recusa-se a prosseguir em distribuições fora da família RHEL 9, para não
    executar comandos dnf em um sistema para o qual o runbook não foi escrito.

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.
        dry_run: Se True, apenas registra o que seria feito.

    Raises:
        SetupError: Se o SO não for suportado ou a instalação falhar.
    """
    logger.info("Verificando/instalando pré-requisitos do SO...")

    try:
        os_release = _read_os_release()
    except Exception as e:
        raise SetupError(f"Não foi possível identificar o sistema operacional: {e}")

    os_id = os_release.get("ID", "").lower()
    if os_id not in SUPPORTED_OS_IDS:
        raise SetupError(
            f"SO '{os_id}' fora do escopo do runbook (esperado: {sorted(SUPPORTED_OS_IDS)}). "
            "Instalação interrompida antes de qualquer alteração."
        )

    # dnf install é idempotente: pacotes já presentes são reportados e ignorados.
    _run(["dnf", "install", "-y"] + OS_PREREQ_PACKAGES, logger, dry_run)
    logger.info("Pré-requisitos do SO instalados.")


# O postinstall.pl recusa reexecução em um servidor já configurado, saindo com
# código 1 e a mensagem abaixo. Tratar isso como falha tornaria `setup --apply`
# não idempotente.
POSTINSTALL_ALREADY_CONFIGURED = "is successfully configured"


def _ksc_is_configured() -> bool:
    """True se o Administration Server já tiver sido configurado neste host.

    A presença da unidade systemd do servidor é o indicador: ela só é criada
    pelo postinstall.pl, não pela instalação do RPM.
    """
    try:
        stdout, _, rc = run_command(
            ["systemctl", "list-unit-files", "kladminserver_srv.service"], check=False
        )
        return rc == 0 and "kladminserver_srv.service" in (stdout or "")
    except Exception:
        return False


def _account_exists(kind: str, name: str) -> bool:
    """True se o usuário ('passwd') ou grupo ('group') já existir no sistema."""
    try:
        _, _, rc = run_command(["getent", kind, name], check=False)
        return rc == 0
    except Exception:
        return False


def _ensure_ksc_accounts(logger: logging.Logger, dry_run: bool = False) -> None:
    """Cria o grupo administrativo e a conta de serviço exigidos pelo instalador.

    O postinstall.pl valida a existência do grupo informado em
    KLSRV_UNATT_KLADMINSGROUP e da conta de serviço, mas não os cria. Sem este
    passo a instalação silenciosa aborta antes de qualquer alteração.

    Idempotente: contas já existentes são preservadas como estão.
    """
    if dry_run:
        logger.info(
            f"[CHECK] Seriam garantidos o grupo '{KSC_ADMINS_GROUP}' e a conta de "
            f"serviço '{KSC_SERVICE_USER}' antes do instalador."
        )
        return

    if _account_exists("group", KSC_ADMINS_GROUP):
        logger.info(f"Grupo '{KSC_ADMINS_GROUP}' já existe.")
    else:
        _run(["groupadd", "--system", KSC_ADMINS_GROUP], logger)

    if _account_exists("passwd", KSC_SERVICE_USER):
        logger.info(f"Conta de serviço '{KSC_SERVICE_USER}' já existe.")
    else:
        _run(
            [
                "useradd",
                "--system",
                "--gid",
                KSC_ADMINS_GROUP,
                "--home-dir",
                KSC_DATA_DIR,
                "--no-create-home",
                "--shell",
                "/sbin/nologin",
                KSC_SERVICE_USER,
            ],
            logger,
        )


def _psql(
    sql: str, logger: logging.Logger, dry_run: bool, redacted: bool = False
) -> None:
    """Executa SQL como o usuário postgres, com o statement vindo do stdin.

    O SQL nunca é passado em argv, para não aparecer na lista de processos do
    servidor quando contiver senhas.
    """
    _run(
        ["runuser", "-u", "postgres", "--", "psql", "-v", "ON_ERROR_STOP=1", "-q"],
        logger,
        dry_run,
        input_data=sql,
        redacted=redacted,
    )


def setup_postgres(
    config: KscConfig, logger: logging.Logger, dry_run: bool = False
) -> None:
    """Instala e prepara o PostgreSQL 16 local para o KSC.

    Só atua sobre um PostgreSQL local. Se ``config.db_host`` apontar para um
    host remoto, o provisionamento é considerado externo e o passo apenas
    valida a conectividade declarada pelos pré-checks.

    Cria a role de aplicação e as bases ``ksc`` e ``ksciam`` de forma
    idempotente: um cluster já inicializado não é reinicializado e objetos já
    existentes não são recriados.

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.
        dry_run: Se True, apenas registra o que seria feito.

    Raises:
        SetupError: Se algum comando de provisionamento falhar.
    """
    if config.db_host not in ("127.0.0.1", "localhost", "::1"):
        logger.info(
            f"PostgreSQL remoto declarado em {config.db_host}:{config.db_port}; "
            "provisionamento local ignorado. As bases e a role devem existir previamente."
        )
        return

    logger.info("Configurando PostgreSQL 16 local...")

    _run(["dnf", "install", "-y", PGDG_REPO_RPM], logger, dry_run)
    _run(
        ["dnf", "-qy", "module", "disable", "postgresql"], logger, dry_run, check=False
    )
    _run(["dnf", "install", "-y", "postgresql16-server"], logger, dry_run)

    if Path(PG_DATA_DIR, "PG_VERSION").exists():
        logger.info(f"Cluster já inicializado em {PG_DATA_DIR}; initdb ignorado.")
    else:
        _run([PG_SETUP_BIN, "initdb"], logger, dry_run)

    _run(["systemctl", "enable", "--now", PG_SERVICE], logger, dry_run)

    # Role de aplicação: criada apenas se ausente; a senha vai por stdin.
    role_sql = (
        "DO $$ BEGIN "
        f"IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{config.db_user}') THEN "
        f"CREATE ROLE \"{config.db_user}\" LOGIN PASSWORD '{config.db_password}'; "
        "END IF; END $$;"
    )
    _psql(role_sql, logger, dry_run, redacted=True)

    # O KSC usa duas bases: a operacional (ksc) e a do serviço IAM (ksciam).
    for db_name in ("ksc", config.db_name):
        # CREATE DATABASE não roda dentro de bloco DO; o \gexec do psql executa
        # o comando apenas quando o SELECT retorna linha (base ainda ausente).
        create_sql = (
            f'SELECT \'CREATE DATABASE "{db_name}" OWNER "{config.db_user}"\' '
            f"WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '{db_name}')\n"
            "\\gexec\n"
        )
        _psql(create_sql, logger, dry_run)

    if dry_run:
        logger.info("[CHECK] Simulação do provisionamento do PostgreSQL 16 concluída.")
    else:
        logger.info("PostgreSQL 16 provisionado e preparado.")


def verify_ksc_packages(package_dir: str, logger: logging.Logger) -> None:
    """Verifica a integridade criptográfica SHA-256 dos pacotes RPM antes da instalação.

    Args:
        package_dir: Diretório contendo os arquivos RPM a serem verificados.
        logger: Logger para registro das operações.

    Raises:
        SetupError: Se qualquer pacote reconhecido apresentar hash divergente.
    """
    from .packages import verify_directory

    logger.info(f"Verificando integridade SHA-256 dos pacotes em '{package_dir}'...")
    try:
        results = verify_directory(package_dir)
    except Exception as e:
        raise SetupError(f"Falha ao validar diretório de pacotes '{package_dir}': {e}")

    if results["failed"]:
        failed_files = [item["file"] for item in results["failed"]]
        logger.error(f"Pacotes com checksum divergente detectados: {failed_files}")
        raise SetupError(
            f"Falha de integridade criptográfica nos pacotes: {', '.join(failed_files)}. "
            "Possível corrupção ou adulteração de binários."
        )

    logger.info(
        f"Integridade validada com sucesso: {len(results['verified'])} pacotes certificados."
    )


def build_response_file(config: KscConfig) -> str:
    """Monta o conteúdo do arquivo de respostas KLAUTOANSWERS.

    Fonte única do formato, compartilhada entre a instalação inicial e a
    reconfiguração de um servidor já instalado. Espelha
    ``configs/ksc/ksc_response.txt.template``.

    O formato das chaves KLSRV_UNATT_* é baseado em comportamento observado e
    não em contrato documentado — ver project-review/08-maintainer-questions.md (Q3).

    Args:
        config: Configuração do KSC.

    Returns:
        Conteúdo textual do arquivo de respostas.
    """
    return f"""EULA_ACCEPTED=1
PP_ACCEPTED=1
KSN_ACCEPTED=1
KLSRV_UNATT_DBMS_TYPE=Postgres
KLSRV_UNATT_DBMS_INSTANCE={config.db_host}
KLSRV_UNATT_DBMS_PORT={config.db_port}
KLSRV_UNATT_DBMS_LOGIN={config.db_user}
KLSRV_UNATT_DBMS_PASSWORD={config.db_password}
KLSRV_UNATT_DB_NAME=ksc
KLSRV_UNATT_DBMS_IAM_TYPE=Postgres
KLSRV_UNATT_DBMS_IAM_INSTANCE={config.db_host}
KLSRV_UNATT_DBMS_IAM_PORT={config.db_port}
KLSRV_UNATT_DBMS_IAM_LOGIN={config.db_user}
KLSRV_UNATT_DBMS_IAM_PASSWORD={config.db_password}
KLSRV_UNATT_DB_IAM_NAME={config.db_name}
KLSRV_UNATT_SERVERADDRESS={config.ksc_fqdn}
KLSRV_UNATT_IAM_ADDRESS=127.0.0.1
KLSRV_UNATT_KLSVCUSER={KSC_SERVICE_USER}
KLSRV_UNATT_KLADMINSGROUP={KSC_ADMINS_GROUP}
KLSRV_UNATT_KLIAMUSER={KSC_SERVICE_USER}
KLSRV_UNATT_KLSRVUSER={KSC_SERVICE_USER}
KLSRV_UNATT_KLADMINS_USER={config.ksc_admin_user}
KLSRV_UNATT_KLADMINS_PASSWORD={config.ksc_admin_password}
"""


def _web_console_is_configured(parametros_desejados: str) -> bool:
    """True se o Web Console já estiver configurado com estes mesmos parâmetros.

    Exige as duas condições: a unidade principal existir — ela é criada pelo
    setup.js, não pelo RPM — e o arquivo de parâmetros em uso ser idêntico ao
    que seria gravado. Parâmetros diferentes significam reconfiguração
    intencional, e aí o setup.js precisa mesmo rodar.
    """
    try:
        stdout, _, rc = run_command(
            ["systemctl", "list-unit-files", "KSCWebConsole.service"], check=False
        )
        if rc != 0 or "KSCWebConsole.service" not in (stdout or ""):
            return False
    except Exception:
        return False

    try:
        atual = Path(WEB_CONSOLE_SETUP_FILE).read_text(encoding="utf-8")
    except OSError:
        return False

    return atual.strip() == parametros_desejados.strip()


def build_web_console_setup(config: KscConfig) -> str:
    """Monta o arquivo de parâmetros do Web Console.

    As chaves são as que o próprio setup.js lê. Atenção: o exemplo histórico do
    repositório usava `defaultLanguageId`, `trusted_cert` e `trusted_cert_key`,
    que o instalador ignora — os nomes corretos são `defaultLangId`, `trusted`,
    `certPath` e `keyPath`.

    `acceptEula` aceita o contrato de licença de forma não interativa, em linha
    com o EULA_ACCEPTED=1 já usado no arquivo de respostas do servidor.
    """
    return json.dumps(
        {
            "acceptEula": True,
            "address": config.ksc_fqdn,
            "port": config.web_port,
            "defaultLangId": WEB_CONSOLE_LANG_ID,
            "enableLog": True,
            "trusted": "",
            "certPath": "",
            "keyPath": "",
        },
        indent=2,
    )


def configure_web_console(
    config: KscConfig, logger: logging.Logger, dry_run: bool = False
) -> None:
    """Configura e sobe o KSC Web Console.

    Instalar o RPM não basta: a configuração é feita pelo setup.js, que lê o
    arquivo de parâmetros em /etc e cria as unidades systemd, os certificados e
    as contas de serviço próprias do componente.

    Raises:
        SetupError: Se a gravação do arquivo ou a configuração falharem.
    """
    logger.info("Configurando o KSC Web Console...")

    desejado = build_web_console_setup(config)

    if dry_run:
        logger.info(
            f"[CHECK] Seria gravado {WEB_CONSOLE_SETUP_FILE} (modo 0600) com porta "
            f"{config.web_port} e executado: {WEB_CONSOLE_DIR}/node setup.js"
        )
        return

    # Reexecutar o setup.js regenera o certificado TLS e recria as contas de
    # serviço com novos nomes. Em um Web Console já configurado com os mesmos
    # parâmetros isso é puro dano: invalida a confiança de qualquer cliente que
    # já tenha aceitado o certificado, sem que a auditoria acuse mudança alguma.
    if _web_console_is_configured(desejado):
        logger.info(
            "Web Console já configurado com estes parâmetros; setup.js ignorado "
            "para preservar o certificado e as contas de serviço existentes."
        )
        for unit in WEB_CONSOLE_SERVICES:
            _run(["systemctl", "enable", "--now", unit], logger, check=False)
        return

    try:
        Path(WEB_CONSOLE_SETUP_FILE).write_text(desejado, encoding="utf-8")
        os.chmod(WEB_CONSOLE_SETUP_FILE, 0o600)
    except OSError as e:
        raise SetupError(f"Falha ao gravar {WEB_CONSOLE_SETUP_FILE}: {e}")

    # A unidade criada pelo instalador roda com um usuário sem privilégio e sem
    # CAP_NET_BIND_SERVICE: sem esta capacidade o serviço não consegue abrir
    # portas abaixo de 1024 e fica reiniciando sem nunca escutar.
    if config.web_port < 1024:
        try:
            Path(WEB_CONSOLE_DROPIN_DIR).mkdir(parents=True, exist_ok=True)
            Path(WEB_CONSOLE_DROPIN_DIR, WEB_CONSOLE_DROPIN_NAME).write_text(
                "[Service]\n"
                "AmbientCapabilities=CAP_NET_BIND_SERVICE\n"
                "CapabilityBoundingSet=CAP_NET_BIND_SERVICE\n",  # pragma: allowlist secret
                encoding="utf-8",
            )
            logger.info(
                f"Drop-in de capacidade gravado para a porta privilegiada {config.web_port}."
            )
        except OSError as e:
            raise SetupError(f"Falha ao gravar o drop-in do Web Console: {e}")
        _run(["systemctl", "daemon-reload"], logger)

    # O setup.js precisa ser executado a partir do diretório do componente.
    _run(
        [
            "sh",
            "-c",
            f"cd {WEB_CONSOLE_DIR} && ./node setup.js {WEB_CONSOLE_SETUP_FILE}",
        ],
        logger,
    )

    for unit in WEB_CONSOLE_SERVICES:
        _run(["systemctl", "reset-failed", unit], logger, check=False)
        _run(["systemctl", "enable", "--now", unit], logger, check=False)

    logger.info(f"Web Console configurado na porta {config.web_port}.")


def _resolve_rpms(package_dir: str) -> List[str]:
    """Localiza os RPMs do KSC no diretório, em ordem de dependência.

    Raises:
        SetupError: Se algum pacote obrigatório estiver ausente.
    """
    available = sorted(str(p) for p in Path(package_dir).rglob("*.rpm"))
    resolved = []
    for prefix in KSC_RPM_PREFIXES:
        matches = [p for p in available if Path(p).name.startswith(prefix)]
        if not matches:
            raise SetupError(
                f"Pacote obrigatório '{prefix}*.rpm' não encontrado em '{package_dir}'. "
                "Use 'kscctl packages --download' ou copie os RPMs oficiais para o diretório."
            )
        if len(matches) > 1:
            raise SetupError(
                f"Mais de um pacote '{prefix}*.rpm' em '{package_dir}': {matches}. "
                "Mantenha apenas uma versão por diretório de instalação."
            )
        resolved.append(matches[0])
    return resolved


def _write_response_file(content: str) -> str:
    """Grava o arquivo de respostas em um arquivo temporário com modo 0600."""
    fd, path = tempfile.mkstemp(prefix="ksc_answers_", suffix=".txt")
    try:
        os.fchmod(fd, 0o600)
    except (AttributeError, OSError):
        os.chmod(path, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


def install_ksc_server(
    config: KscConfig, logger: logging.Logger, dry_run: bool = False
) -> None:
    """Instala o KSC Server, o Network Agent e o Web Console via RPM silencioso.

    A verificação de integridade SHA-256 dos pacotes é obrigatória e ocorre
    antes de qualquer instalação (Zero Trust Gate). Em seguida o
    ``postinstall.pl`` é executado em modo não interativo, com o arquivo de
    respostas gravado em modo 0600 e removido ao final, mesmo em caso de erro.

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.
        dry_run: Se True, apenas registra o que seria feito.

    Raises:
        SetupError: Se a verificação, a instalação ou o postinstall falharem.
    """
    packages_dir = getattr(config, "packages_dir", None) or os.environ.get(
        "KSC_PACKAGES_DIR"
    )
    if not packages_dir:
        if dry_run:
            # Em simulação, a ausência dos pacotes é condição do ambiente, não
            # defeito de configuração: avisa e segue, sem mascarar o gate real.
            logger.warning(
                "[CHECK] KSC_PACKAGES_DIR não configurado: a verificação de integridade "
                "e a instalação dos RPMs não puderam ser simuladas. Em --apply isto é erro fatal."
            )
            return
        raise SetupError(
            "KSC_PACKAGES_DIR não configurado. A verificação prévia de integridade dos pacotes é obrigatória para instalação."
        )

    if dry_run:
        try:
            verify_ksc_packages(packages_dir, logger)
            rpms = _resolve_rpms(packages_dir)
        except SetupError as e:
            logger.warning(
                f"[CHECK] Simulação da instalação dos pacotes indisponível: {e}"
            )
            return
    else:
        verify_ksc_packages(packages_dir, logger)
        rpms = _resolve_rpms(packages_dir)
    logger.info(f"Pacotes a instalar: {[Path(p).name for p in rpms]}")
    _run(["dnf", "install", "-y"] + rpms, logger, dry_run)

    _ensure_ksc_accounts(logger, dry_run)

    if dry_run:
        logger.info(
            "[CHECK] Seria gravado o arquivo de respostas KLAUTOANSWERS em modo 0600 "
            f"e executado: {KSC_POSTINSTALL}"
        )
    else:
        if _ksc_is_configured():
            logger.info(
                "Administration Server já configurado neste host; postinstall.pl ignorado. "
                "Para reconfigurar, use 'kscctl' com o fluxo de reconfiguração."
            )
            answers_path = None
        else:
            answers_path = _write_response_file(build_response_file(config))
        try:
            if answers_path is not None:
                logger.info(
                    f"Arquivo de respostas gerado em {answers_path} (modo 0600)."
                )
                rc = _run(
                    [
                        "env",
                        f"KLAUTOANSWERS={answers_path}",
                        "perl",
                        KSC_POSTINSTALL,
                    ],
                    logger,
                    dry_run=False,
                    check=False,
                )
                if rc != 0:
                    raise SetupError(
                        f"postinstall.pl falhou (rc={rc}). Consulte o log desta execução "
                        "e docs/10-troubleshooting.md."
                    )
        finally:
            if answers_path is not None:
                try:
                    os.remove(answers_path)
                    logger.info("Arquivo de respostas temporário removido.")
                except OSError as e:
                    logger.warning(f"Falha ao remover {answers_path}: {e}")

    logger.info(
        "Nota sobre LD_LIBRARY_PATH: O KSC no Linux muitas vezes exige bibliotecas. A recomendação DEVSECOPS é usar Environment=LD_LIBRARY_PATH=... no arquivo de serviço systemd, nunca em /etc/profile ou /etc/environment, para evitar vazamento global."
    )


def post_install_hardening(
    config: KscConfig, logger: logging.Logger, dry_run: bool = False
) -> None:
    """Aplica hardening pós-instalação: permissões, SELinux, LD_LIBRARY_PATH e serviços.

    O ``LD_LIBRARY_PATH`` é aplicado como drop-in do systemd na unidade do
    Administration Server, e não em ``/etc/profile`` ou ``/etc/environment``,
    para não vazar o caminho das bibliotecas do KSC para o sistema inteiro.

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.
        dry_run: Se True, apenas registra o que seria feito.

    Raises:
        SetupError: Se um comando obrigatório de hardening falhar.
    """
    logger.info("Aplicando hardening pós-instalação...")

    # Remover o acesso de "outros" exige antes garantir o acesso do grupo de
    # serviço: os binários em /opt/kaspersky pertencem a root e os serviços
    # rodam como o usuário `ksc`. Um `chmod -R o-rwx` isolado tira do serviço
    # até a travessia do diretório e o klserver passa a falhar com
    # "Permission denied" (status 203/EXEC).
    _run(
        ["chgrp", "-R", KSC_ADMINS_GROUP, "/opt/kaspersky"],
        logger,
        dry_run,
        check=False,
    )
    _run(["chmod", "-R", "g+rX,o-rwx", "/opt/kaspersky"], logger, dry_run, check=False)

    # O diretório de dados NÃO recebe chmod recursivo. O instalador cria ali
    # subdiretórios já restritos e contas de serviço próprias, de nomes
    # gerados aleatoriamente e fora do grupo administrativo — o Web Console é
    # uma delas. Fechar o acesso de "outros" recursivamente derrubava tanto o
    # klserver (203/EXEC) quanto o Web Console (200/CHDIR).
    #
    # O que se faz aqui é apenas dar ao grupo administrativo o acesso ao
    # diretório-raiz, preservando a travessia de que as demais contas dependem.
    _run(["chgrp", KSC_ADMINS_GROUP, KSC_DATA_DIR], logger, dry_run, check=False)
    _run(["chmod", "g+rx,o+rx", KSC_DATA_DIR], logger, dry_run, check=False)

    dropin_file = str(Path(SYSTEMD_DROPIN_DIR) / SYSTEMD_DROPIN_NAME)
    dropin_content = f"[Service]\nEnvironment=LD_LIBRARY_PATH={KSC_LIB_DIR}\n"

    if dry_run:
        logger.info(
            f"[CHECK] Seria criado o drop-in systemd {dropin_file} com "
            f"Environment=LD_LIBRARY_PATH={KSC_LIB_DIR}"
        )
    else:
        try:
            Path(SYSTEMD_DROPIN_DIR).mkdir(parents=True, exist_ok=True)
            Path(dropin_file).write_text(dropin_content, encoding="utf-8")
            os.chmod(dropin_file, 0o644)
            logger.info(f"Drop-in systemd gravado em {dropin_file}.")
        except OSError as e:
            raise SetupError(f"Falha ao gravar drop-in systemd {dropin_file}: {e}")

    _run(["restorecon", "-Rv", "/opt/kaspersky"], logger, dry_run, check=False)
    _run(["restorecon", "-Rv", KSC_DATA_DIR], logger, dry_run, check=False)

    _run(["systemctl", "daemon-reload"], logger, dry_run)
    for unit in KSC_SERVICES:
        # Uma unidade que estourou o limite de reinícios permanece em 'failed' e
        # ignora o enable --now seguinte; o reset-failed limpa esse estado.
        _run(["systemctl", "reset-failed", unit], logger, dry_run, check=False)
        _run(["systemctl", "enable", "--now", unit], logger, dry_run, check=False)

    if not dry_run:
        inactive = [unit for unit in KSC_SERVICES if not _unit_is_active(unit)]
        if inactive:
            raise SetupError(
                f"Serviços do KSC não ficaram ativos após o hardening: {inactive}. "
                "Consulte docs/10-troubleshooting.md."
            )

    if dry_run:
        logger.info("[CHECK] Simulação do hardening pós-instalação concluída.")
    else:
        logger.info("Hardening pós-instalação concluído; serviços do KSC ativos.")


def perform_precheck_only(config: KscConfig, logger: logging.Logger) -> CheckResult:
    """Executa apenas os pré-checks sem iniciar a instalação. Retorna CheckResult.

    Em um host onde o KSC já está instalado, a verificação de portas livres é
    omitida: as portas estão ocupadas pelo próprio produto, e tratá-las como
    falha crítica impediria a reexecução de `setup --apply`.

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.

    Returns:
        CheckResult com os resultados dos pré-checks.
    """
    instalado = _ksc_is_configured()
    if instalado:
        logger.info(
            "KSC já instalado neste host: a verificação de portas livres não se aplica."
        )
    return run_precheck(config, skip_ports=instalado)


def perform_setup(
    config: KscConfig, logger: logging.Logger, dry_run: bool = False
) -> None:
    """Orquestra a instalação garantindo o ciclo seguro do SELinux.

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.
        dry_run: Se True, executa a sequência completa sem alterar o sistema.

    Raises:
        SetupError: Se os pré-checks falharem criticamente ou algum passo falhar.
    """
    original_selinux = _get_selinux_mode()
    selinux_changed = False

    try:
        # Prechecks
        result = perform_precheck_only(config, logger)
        if result.has_critical:
            raise SetupError(
                "Prechecks falharam criticamente. Interrompendo instalação."
            )

        # Temporariamente permissivo para a instalação não falhar no setup de binários
        if original_selinux == "enforcing" and not dry_run:
            logger.info(
                "Desabilitando SELinux (permissive) temporariamente para a instalação do KSC."
            )
            _set_selinux_mode("0", logger)
            selinux_changed = True

        ensure_os_prereqs(config, logger, dry_run)
        setup_postgres(config, logger, dry_run)
        install_ksc_server(config, logger, dry_run)
        configure_web_console(config, logger, dry_run)
        post_install_hardening(config, logger, dry_run)

    except Exception as e:
        raise SetupError(f"Falha na instalação: {e}")
    finally:
        if selinux_changed:
            logger.info(
                "Restaurando SELinux para o modo enforcing (Segurança por Padrão)."
            )
            _set_selinux_mode("1", logger)
            # Reetiqueta os arquivos criados enquanto o SELinux estava permissivo.
            run_command(["restorecon", "-Rv", "/opt/kaspersky"], check=False)
