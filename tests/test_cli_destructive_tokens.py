# -*- coding: utf-8 -*-
"""Testes de validação contextual de tokens e alvos para operações destrutivas no kscctl (#SEC-06).

Garante que operações com grande impacto (db reset, iam purge-mfa, rollback):
1. Rejeitem execução --apply sem token ou com token inválido.
2. Rejeitem tokens contextuais cujo host alvo não coincida com a configuração ativa.
3. Suportem a flag --confirm-target e rejeitem divergências contra o host configurado.
"""

from unittest.mock import MagicMock, patch
import pytest

from automation.python.config import KscConfig
from automation.python.kscctl import main


@pytest.fixture
def mock_ksc_config(ksc_test_config):
    return ksc_test_config.model_copy(
        update={"ksc_host": "ksc-prod.internal.net", "db_name": "ksc_prod"}
    )


def test_db_reset_rejects_mismatching_contextual_token(mock_ksc_config, monkeypatch, capsys):
    """Garante que 'db reset --apply' rejeite token contextual com host divergente."""
    monkeypatch.setattr("automation.python.config.load_config", lambda: mock_ksc_config)

    ret = main(["db", "reset", "--apply", "--confirm-token", "RESET-CONFIRM:wrong-host.test"])
    assert ret == 3
    captured = capsys.readouterr()
    assert "diverge" in captured.err.lower() or "inválido" in captured.err.lower()


def test_db_reset_rejects_mismatching_confirm_target(mock_ksc_config, monkeypatch, capsys):
    """Garante que 'db reset --apply' rejeite flag --confirm-target com host divergente."""
    monkeypatch.setattr("automation.python.config.load_config", lambda: mock_ksc_config)

    ret = main(["db", "reset", "--apply", "--confirm-token", "RESET-CONFIRM", "--confirm-target", "wrong-host.test"])
    assert ret == 3
    captured = capsys.readouterr()
    assert "diverge" in captured.err.lower()


def test_purge_mfa_rejects_mismatching_contextual_token(mock_ksc_config, monkeypatch, capsys):
    """Garante que 'iam purge-mfa --apply' rejeite token contextual com host divergente."""
    monkeypatch.setattr("automation.python.config.load_config", lambda: mock_ksc_config)

    ret = main(["iam", "purge-mfa", "--apply", "--confirm-token", "PURGE-CONFIRM:wrong-host.test"])
    assert ret == 3
    captured = capsys.readouterr()
    assert "diverge" in captured.err.lower() or "inválido" in captured.err.lower()


def test_rollback_rejects_mismatching_contextual_token(mock_ksc_config, monkeypatch, capsys):
    """Garante que 'rollback --apply' rejeite token contextual com host divergente."""
    monkeypatch.setattr("automation.python.config.load_config", lambda: mock_ksc_config)

    ret = main(["rollback", "--apply", "--confirm-token", "ROLLBACK-CONFIRM:wrong-host.test"])
    assert ret == 3
    captured = capsys.readouterr()
    assert "diverge" in captured.err.lower() or "inválido" in captured.err.lower()


def test_destructive_operations_accept_matching_contextual_tokens(mock_ksc_config, monkeypatch):
    """Garante que operações aceitem tokens contextuais quando o host coincide."""
    monkeypatch.setattr("automation.python.config.load_config", lambda: mock_ksc_config)

    with patch("automation.ops.reset_ksc_databases.reset_ksc_databases") as mock_reset:
        ret = main(["db", "reset", "--apply", "--confirm-token", f"RESET-CONFIRM:{mock_ksc_config.ksc_host}"])
        assert ret == 0
        assert mock_reset.called

    with patch("automation.ops.purge_iam_mfa.purge_iam_mfa") as mock_purge:
        ret = main(["iam", "purge-mfa", "--apply", "--confirm-token", f"PURGE-CONFIRM:{mock_ksc_config.ksc_host}"])
        assert ret == 0
        assert mock_purge.called

    with patch("automation.python.rollback.perform_rollback") as mock_rollback:
        ret = main(["rollback", "--apply", "--confirm-token", f"ROLLBACK-CONFIRM:{mock_ksc_config.ksc_host}"])
        assert ret == 0
        assert mock_rollback.called
