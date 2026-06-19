import pytest
import shlex
from unittest.mock import patch, MagicMock
from automation.ops.reset_ksc_databases import reset_ksc_databases
from automation.python.config import KscConfig


@pytest.fixture
def dummy_config():
    return KscConfig(
        db_host="127.0.0.1",
        db_password="dummy_password",
        db_user='kluser"test',  # Test malicious injection
        ksc_admin_password="dummy_admin_password",
        ksc_host="test.ksc.local",
        ksc_user="testuser",
        ksc_pass="testpass",
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
