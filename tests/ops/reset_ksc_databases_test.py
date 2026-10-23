import pytest
import shlex
from unittest.mock import patch, MagicMock
from automation.ops.purge_iam_mfa import OpsError
from automation.ops.reset_ksc_databases import reset_ksc_databases
from automation.python.config import KscConfig
from automation.python.credentials import (
    generate_password,
    generate_synthetic_fqdn,
    generate_username,
)


@pytest.fixture
def dummy_config():
    # Credenciais geradas em vez de literais. O db_user mantém a aspa
    # deliberadamente: o objetivo do teste é provar que a injeção é escapada.
    return KscConfig(
        db_host="127.0.0.1",
        db_password=generate_password(),
        db_user='kluser"test',  # Test malicious injection
        ksc_admin_password=generate_password(),
        ksc_host=generate_synthetic_fqdn(),
        ksc_user=generate_username(),
        ksc_pass=generate_password(),
    )


@patch("automation.ops.reset_ksc_databases.connect_ksc_host")
@patch("automation.ops.reset_ksc_databases.run_remote_sudo")
def test_reset_ksc_databases_secure_quoting(
    mock_run_remote_sudo, mock_connect, dummy_config
):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("stdout", "stderr", 0)

    reset_ksc_databases(dummy_config, apply=True)

    calls = mock_run_remote_sudo.call_args_list
    # 1 stop + 3 queries * 2 databases
    assert len(calls) == 7

    assert (
        calls[0][0][1] == "systemctl stop kladminserver_srv ksc-web-console kliam_srv"
    )

    dbs = ["ksc", "ksciam"]
    call_idx = 1

    for db in dbs:
        term_query = (
            f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
            f"FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{db}' "
            f"AND pid <> pg_backend_pid();"
        )
        assert calls[call_idx][0][1] == f"-u postgres psql -c {shlex.quote(term_query)}"
        call_idx += 1

        drop_query = f"DROP DATABASE {db};"
        assert calls[call_idx][0][1] == f"-u postgres psql -c {shlex.quote(drop_query)}"
        call_idx += 1

        safe_db_user = dummy_config.db_user.replace('"', '""')
        create_query = f'CREATE DATABASE "{db}" OWNER "{safe_db_user}";'
        assert (
            calls[call_idx][0][1] == f"-u postgres psql -c {shlex.quote(create_query)}"
        )
        call_idx += 1


@patch("automation.ops.reset_ksc_databases.connect_ksc_host")
@patch("automation.ops.reset_ksc_databases.run_remote_sudo")
def test_reset_ksc_databases_check_only(mock_run_remote_sudo, mock_connect, dummy_config):
    """Garante que no modo check-only nenhuma conexão SSH ou comando remoto seja executado."""
    reset_ksc_databases(dummy_config, apply=False)

    mock_connect.assert_not_called()
    mock_run_remote_sudo.assert_not_called()


@patch("automation.ops.reset_ksc_databases.connect_ksc_host")
@patch("automation.ops.reset_ksc_databases.run_remote_sudo")
def test_reset_ksc_databases_stop_failure_raises_ops_error(mock_run_remote_sudo, mock_connect, dummy_config):
    """Garante que falha ao parar os serviços KSC dispara OpsError."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("", "systemctl: error stopping service", 1)

    with pytest.raises(OpsError, match="Falha ao parar serviços KSC"):
        reset_ksc_databases(dummy_config, apply=True)


@patch("automation.ops.reset_ksc_databases.connect_ksc_host")
@patch("automation.ops.reset_ksc_databases.run_remote_sudo")
def test_reset_ksc_databases_drop_failure_raises_ops_error(mock_run_remote_sudo, mock_connect, dummy_config):
    """Garante que falha no DROP DATABASE dispara OpsError."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    # 1: stop_services (ok), 2: terminate (ok), 3: drop database (falha)
    mock_run_remote_sudo.side_effect = [
        ("stdout", "", 0),
        ("stdout", "", 0),
        ("", "ERROR: database ksc is being accessed by other users", 1),
    ]

    with pytest.raises(OpsError, match="Falha no DROP DATABASE"):
        reset_ksc_databases(dummy_config, apply=True)


@patch("automation.ops.reset_ksc_databases.connect_ksc_host")
@patch("automation.ops.reset_ksc_databases.run_remote_sudo")
def test_reset_ksc_databases_create_failure_raises_ops_error(mock_run_remote_sudo, mock_connect, dummy_config):
    """Garante que falha no CREATE DATABASE dispara OpsError."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    # 1: stop (ok), 2: terminate (ok), 3: drop (ok), 4: create (falha)
    mock_run_remote_sudo.side_effect = [
        ("stdout", "", 0),
        ("stdout", "", 0),
        ("stdout", "", 0),
        ("", "ERROR: role does not exist", 1),
    ]

    with pytest.raises(OpsError, match="Falha no CREATE DATABASE"):
        reset_ksc_databases(dummy_config, apply=True)


@patch("automation.ops.reset_ksc_databases.connect_ksc_host")
@patch("automation.ops.reset_ksc_databases.run_remote_sudo")
def test_reset_ksc_databases_client_closed_in_finally(mock_run_remote_sudo, mock_connect, dummy_config):
    """Garante que client.close() é chamado mesmo quando uma exceção ocorre durante o reset."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.side_effect = RuntimeError("Erro de conexão SSH")

    with pytest.raises(OpsError):
        reset_ksc_databases(dummy_config, apply=True)

    mock_client.close.assert_called_once()
