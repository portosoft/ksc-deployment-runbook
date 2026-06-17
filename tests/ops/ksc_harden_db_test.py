import pytest
from unittest.mock import MagicMock, patch
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
    from automation.ops.ksc_harden_db import apply_hardening

    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote.return_value = (
        "max_connections = 1000\nshared_preload_libraries = 'pg_stat_statements'\n",
        "",
        0,
    )

    apply_hardening(ksc_config, apply=False)

    mock_connect.assert_called_once()
    mock_run_remote.assert_called_once()
    mock_client.close.assert_called_once()


@patch("automation.ops.ksc_harden_db.connect_ksc_host")
@patch("automation.ops.ksc_harden_db.run_remote_sudo")
def test_apply_hardening_already_applied(mock_run_remote, mock_connect, ksc_config):
    from automation.ops.ksc_harden_db import apply_hardening

    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote.return_value = (
        "max_connections = 1000\nshared_preload_libraries = 'pg_stat_statements'\n",
        "",
        0,
    )

    apply_hardening(ksc_config, apply=True)

    mock_client.close.assert_called_once()


@patch("automation.ops.ksc_harden_db.connect_ksc_host")
@patch("automation.ops.ksc_harden_db.run_remote_sudo")
@patch("automation.ops.ksc_harden_db.run_remote_sudo_batch")
def test_apply_hardening_apply_changes(mock_run_batch, mock_run_remote, mock_connect, ksc_config):
    from automation.ops.ksc_harden_db import apply_hardening

    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote.return_value = (
        "max_connections = 100\n#shared_preload_libraries = ''\n",
        "",
        0,
    )
    mock_run_batch.return_value = (0, "ok", "", [])

    apply_hardening(ksc_config, apply=True)

    assert mock_client.close.called
