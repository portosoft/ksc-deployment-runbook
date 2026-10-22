import pytest
from unittest.mock import MagicMock, patch
from automation.python.config import KscConfig
from automation.python.credentials import generate_password
from automation.ops.purge_iam_mfa import OpsError


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
        ksc_admin_user="KLAdmins",
    )


@patch("automation.ops.fix_ksc_auth.connect_ksc_host")
@patch("automation.ops.fix_ksc_auth.run_remote_sudo")
def test_fix_ksc_auth_apply_success(mock_run_remote, mock_connect, ksc_config):
    from automation.ops.fix_ksc_auth import fix_ksc_auth

    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote.return_value = ("ok", "", 0)

    fix_ksc_auth(ksc_config, apply=True)

    mock_connect.assert_called_once_with(
        ksc_config.ksc_host, ksc_config.ksc_user, ksc_config.ksc_pass
    )
    mock_run_remote.assert_called_once()
    mock_client.close.assert_called_once()


@patch("automation.ops.fix_ksc_auth.connect_ksc_host")
@patch("automation.ops.fix_ksc_auth.run_remote_sudo")
def test_fix_ksc_auth_apply_failure(mock_run_remote, mock_connect, ksc_config):
    from automation.ops.fix_ksc_auth import fix_ksc_auth

    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote.return_value = ("", "error", 1)

    with pytest.raises(OpsError, match="kladduser remoto falhou"):
        fix_ksc_auth(ksc_config, apply=True)

    mock_client.close.assert_called_once()


def test_fix_ksc_auth_check_only(ksc_config):
    from automation.ops.fix_ksc_auth import fix_ksc_auth

    result = fix_ksc_auth(ksc_config, apply=False)
    assert result is None
