# -*- coding: utf-8 -*-
"""Testes do rollback (#223).

Nenhum teste toca o sistema: todos os comandos são interceptados.
"""

import logging

import pytest

from automation.python import rollback
from automation.python.rollback import KSC_RPMS, perform_rollback, verify_rollback


@pytest.fixture
def logger():
    log = logging.getLogger("test.rollback")
    log.addHandler(logging.NullHandler())
    return log


@pytest.fixture
def recorded(monkeypatch):
    """Intercepta run_command em rollback.py e em setup_steps (via _run)."""
    calls = []

    def fake_run_command(cmd, check=True, capture_output=True, env=None, input_data=None):
        calls.append({"cmd": cmd, "input": input_data})
        # 'rpm -q <pkg>' responde que o pacote está instalado; as demais, sucesso.
        return ("", "", 0)

    monkeypatch.setattr(rollback, "run_command", fake_run_command)
    from automation.python import setup_steps

    monkeypatch.setattr(setup_steps, "run_command", fake_run_command)
    return calls


def _cmds(calls):
    return [" ".join(c["cmd"]) for c in calls]


def test_rollback_removes_every_ksc_package(recorded, logger, ksc_test_config):
    """O procedimento manual esquecia o klnagent64, que sobrevivia ao rollback."""
    perform_rollback(ksc_test_config, logger)

    remocao = next(c for c in _cmds(recorded) if c.startswith("dnf remove -y"))
    for pacote in KSC_RPMS:
        assert pacote in remocao
    assert "klnagent64" in remocao


def test_rollback_drops_both_databases_and_the_configured_role(
    recorded, logger, ksc_test_config
):
    """O procedimento manual citava só 'ksc' e uma role inexistente."""
    perform_rollback(ksc_test_config, logger)

    sql = " ".join(c["input"] or "" for c in recorded)
    assert 'DROP DATABASE IF EXISTS "ksc"' in sql
    assert 'DROP DATABASE IF EXISTS "ksciam"' in sql
    assert f'DROP ROLE IF EXISTS "{ksc_test_config.db_user}"' in sql


def test_rollback_terminates_connections_before_dropping(recorded, logger, ksc_test_config):
    """Uma sessão remanescente faz o DROP DATABASE falhar."""
    perform_rollback(ksc_test_config, logger)

    entradas = [c["input"] for c in recorded if c["input"]]
    kill = next(i for i, t in enumerate(entradas) if "pg_terminate_backend" in t)
    drop = next(i for i, t in enumerate(entradas) if "DROP DATABASE" in t)
    assert kill < drop


def test_rollback_preserves_remote_database(recorded, logger, ksc_test_config):
    """Banco remoto não é do runbook: remover é decisão do administrador dele."""
    remoto = ksc_test_config.model_copy(update={"db_host": "db.interno.test"})
    perform_rollback(remoto, logger)

    sql = " ".join(c["input"] or "" for c in recorded)
    assert "DROP DATABASE" not in sql
    assert "DROP ROLE" not in sql


def test_rollback_removes_accounts_after_files(monkeypatch, recorded, logger, ksc_test_config):
    """Remover as contas antes deixaria os arquivos sem dono conhecido."""
    monkeypatch.setattr(rollback.Path, "exists", lambda self: True)
    perform_rollback(ksc_test_config, logger)

    cmds = _cmds(recorded)
    rm = max(i for i, c in enumerate(cmds) if c.startswith("rm -rf"))
    userdel = next(i for i, c in enumerate(cmds) if c.startswith("userdel"))
    assert rm < userdel


def test_rollback_removes_systemd_dropins(monkeypatch, recorded, logger, ksc_test_config):
    """Drop-ins sobreviviam às unidades que estendiam."""
    monkeypatch.setattr(rollback.Path, "exists", lambda self: True)
    perform_rollback(ksc_test_config, logger)

    cmds = _cmds(recorded)
    assert any("kladminserver_srv.service.d" in c for c in cmds)
    assert any("KSCWebConsole.service.d" in c for c in cmds)
    assert "systemctl daemon-reload" in cmds


def test_dry_run_changes_nothing(recorded, logger, ksc_test_config):
    perform_rollback(ksc_test_config, logger, dry_run=True)

    destrutivos = [
        c
        for c in _cmds(recorded)
        if c.startswith(("rm -rf", "userdel", "groupdel", "dnf remove"))
    ]
    assert destrutivos == []


def test_verify_reports_leftovers(monkeypatch, logger):
    """A verificação é o que transforma 'rodou' em 'ficou limpo'."""
    monkeypatch.setattr(
        rollback, "run_command", lambda cmd, **kw: ("", "", 0 if cmd[0] == "rpm" else 1)
    )
    monkeypatch.setattr(rollback.Path, "exists", lambda self: False)
    monkeypatch.setattr(rollback, "_account_exists", lambda kind, name: False)
    monkeypatch.setattr(rollback, "_existing_units", lambda units: [])

    residuos = verify_rollback(logger)

    # Com 'rpm -q' retornando 0, os três pacotes constam como instalados.
    assert len(residuos) == len(KSC_RPMS)
    assert all("pacote instalado" in r for r in residuos)
