import pytest
import shlex

from unittest.mock import patch, MagicMock
from automation.ops.purge_iam_mfa import purge_iam_mfa
from automation.python.config import KscConfig


@pytest.fixture
def dummy_config():
    return KscConfig(
        db_host="127.0.0.1",
        db_password="dummy_password",
        ksc_admin_password="dummy_admin_password",
        ksc_host="test.ksc.local",
        ksc_user="testuser",
        ksc_pass="testpass",
    )


@patch("automation.ops.purge_iam_mfa.connect_ksc_host")
@patch("automation.ops.purge_iam_mfa.run_remote_sudo")
def test_purge_iam_mfa_secure_quoting(mock_run_remote_sudo, mock_connect, dummy_config):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("stdout", "stderr", 0)

    purge_iam_mfa(dummy_config, apply=True)

    expected_queries = [
        "TRUNCATE iam.authentication_factors CASCADE;",
        "TRUNCATE iam.authentication_factors_secret CASCADE;",
        "TRUNCATE iam.authentication_factors_totp_settings CASCADE;",
    ]

    calls = mock_run_remote_sudo.call_args_list
    assert len(calls) == 4  # 3 queries + 1 restart

    for i, q in enumerate(expected_queries):
        expected_cmd = f"-u postgres psql -d ksciam -c {shlex.quote(q)}"
        assert calls[i][0][1] == expected_cmd
        assert calls[i][0][2] == "testpass"

    # Test the restart command
    assert (
        calls[3][0][1]
        == "systemctl restart kladminserver_srv kliam_srv ksc-web-console"
    )
