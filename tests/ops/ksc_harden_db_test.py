import shlex
from unittest.mock import MagicMock, patch

import pytest

from automation.ops.ksc_harden_db import apply_hardening
from automation.ops.purge_iam_mfa import OpsError
from automation.python.config import KscConfig
from automation.python.credentials import generate_password


@pytest.fixture
def ksc_config():
    return KscConfig(
        db_host="127.0.0.1",
        db_port=5432,
        db_password=generate_password(),
        ksc_admin_password=generate_password(),
        ksc_host="127.0.0.1",
        ksc_user="suporte",
        ksc_pass=generate_password(),
    )


@patch("automation.ops.ksc_harden_db.connect_ksc_host")
@patch("automation.ops.ksc_harden_db.run_remote_sudo")
def test_apply_hardening_check_mode(mock_run_remote, mock_connect, ksc_config):
    """Garante que em modo check nenhuma conexão SSH ou comando remoto seja executado."""
    apply_hardening(ksc_config, apply=False)

    mock_connect.assert_not_called()
    mock_run_remote.assert_not_called()


@patch("automation.ops.ksc_harden_db.connect_ksc_host")
@patch("automation.ops.ksc_harden_db.run_remote_sudo")
def test_apply_hardening_executes_alter_system_sql(
    mock_run_remote, mock_connect, ksc_config
):
    """Garante a aplicação de parâmetros via ALTER SYSTEM e SELECT pg_reload_conf()."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote.return_value = ("stdout", "", 0)

    apply_hardening(ksc_config, apply=True)

    expected_queries = [
        "ALTER SYSTEM SET max_connections = 1000;",
        "ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';",
        "SELECT pg_reload_conf();",
    ]

    calls = mock_run_remote.call_args_list
    assert len(calls) == 4  # 3 queries SQL + 1 restart do postgresql-16

    for i, q in enumerate(expected_queries):
        expected_cmd = f"-u postgres psql -c {shlex.quote(q)}"
        assert calls[i][0][1] == expected_cmd
        assert calls[i][0][2] == ksc_config.ksc_pass

    assert calls[3][0][1] == "systemctl restart postgresql-16"
    assert calls[3][0][2] == ksc_config.ksc_pass
    mock_client.close.assert_called_once()


@patch("automation.ops.ksc_harden_db.connect_ksc_host")
@patch("automation.ops.ksc_harden_db.run_remote_sudo")
def test_apply_hardening_sql_failure_raises_ops_error(
    mock_run_remote, mock_connect, ksc_config
):
    """Garante que falha na query SQL remota dispara OpsError."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote.return_value = ("", "ERROR: permission denied to alter system", 1)

    with pytest.raises(OpsError, match="Falha ao executar query no Postgres"):
        apply_hardening(ksc_config, apply=True)

    mock_client.close.assert_called_once()


@patch("automation.ops.ksc_harden_db.connect_ksc_host")
@patch("automation.ops.ksc_harden_db.run_remote_sudo")
def test_apply_hardening_restart_failure_raises_ops_error(
    mock_run_remote, mock_connect, ksc_config
):
    """Garante que falha no restart do postgresql-16 dispara OpsError."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    # 3 SQL queries ok, restart falha
    mock_run_remote.side_effect = [
        ("stdout", "", 0),
        ("stdout", "", 0),
        ("stdout", "", 0),
        ("", "Job for postgresql-16.service failed", 1),
    ]

    with pytest.raises(OpsError, match="Falha ao reiniciar o serviço postgresql-16"):
        apply_hardening(ksc_config, apply=True)

    mock_client.close.assert_called_once()


@patch("automation.ops.ksc_harden_db.connect_ksc_host")
@patch("automation.ops.ksc_harden_db.run_remote_sudo")
def test_apply_hardening_client_closed_in_finally(
    mock_run_remote, mock_connect, ksc_config
):
    """Garante que client.close() é chamado mesmo quando ocorre uma exceção."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote.side_effect = RuntimeError("Falha de conexão SSH")

    with pytest.raises(OpsError):
        apply_hardening(ksc_config, apply=True)

    mock_client.close.assert_called_once()
