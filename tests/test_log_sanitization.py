# -*- coding: utf-8 -*-
"""Testes de sanitização de segredos em logs de evidência (#237 / L-08).

Garante que nenhuma credencial ou senha configurada (KSC_DB_PASS, KSC_ADMIN_PASS, KSC_PASS)
seja gravada em texto claro nos arquivos de log em evidence/*/run.log ou console.
"""

import logging
from pathlib import Path
import pytest
from automation.python.credentials import generate_password
from automation.python.logging_utils import (
    configure_logger,
    init_evidence_dir,
    log_json,
    sanitize_text,
    set_redaction_secrets,
)


@pytest.fixture
def test_secrets():
    return {
        "db_pass": generate_password(),
        "admin_pass": generate_password(),
        "ssh_pass": generate_password(),
    }


def test_sanitize_text_redacts_registered_secrets(test_secrets):
    """Garante que a função sanitize_text substitua todas as credenciais registradas."""
    set_redaction_secrets(test_secrets.values())

    raw_text = (
        f"Connect psql -p 5432 with password {test_secrets['db_pass']} "
        f"and user KLAdmins password={test_secrets['admin_pass']}"
    )
    sanitized = sanitize_text(raw_text)

    assert test_secrets["db_pass"] not in sanitized
    assert test_secrets["admin_pass"] not in sanitized
    assert "***REDACTED***" in sanitized


def test_evidence_run_log_contains_no_cleartext_passwords(tmp_path, test_secrets, monkeypatch):
    """Garante que log_json e configure_logger nunca gravem credenciais em texto claro no run.log."""
    monkeypatch.chdir(tmp_path)
    set_redaction_secrets(test_secrets.values())

    evidence_dir = init_evidence_dir("deploy")
    test_logger = logging.getLogger(f"ksc_{evidence_dir.name}")
    for h in test_logger.handlers:
        h.close()
    test_logger.handlers.clear()
    logger = configure_logger(evidence_dir)

    # Dispara eventos de log contendo dados sensíveis
    log_json(
        logger,
        "run_command_start",
        cmd=f"psql --password {test_secrets['db_pass']}",
        extra_info=f"admin auth: {test_secrets['admin_pass']}",
    )
    logger.info(f"SSH Auth successful for password: {test_secrets['ssh_pass']}")

    # Lê o arquivo de log gerado
    log_file = evidence_dir / "run.log"
    assert log_file.exists()
    log_content = log_file.read_text(encoding="utf-8")

    for name, secret in test_secrets.items():
        assert secret not in log_content, f"Segredo '{name}' vazou no arquivo run.log!"
    assert "***REDACTED***" in log_content
