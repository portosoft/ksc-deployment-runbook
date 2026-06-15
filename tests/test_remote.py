# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock, patch
from automation.python.remote import connect_ksc_host, run_remote_sudo, run_remote_sudo_batch
from automation.python.config import KscConfig


@pytest.fixture
def dummy_config():
    return KscConfig(
        db_host="127.0.0.1",
        db_port=5432,
        db_name="ksciam",
        db_user="kluser",
        db_password="unittest-dummy-db-pass-000",  # pragma: allowlist secret
        db_sslmode="prefer",
        ksc_admin_password="unittest-dummy-admin-pass-999",  # pragma: allowlist secret
        ksc_license_path=None,
        web_port=443,
        selinux_expected_mode="enforcing",
        ksc_host="127.0.0.1",
        ksc_user="suporte",
        ksc_pass="unittest-dummy-ssh-pass-111",  # pragma: allowlist secret
        ksc_fqdn="kscserver.exemplo.ts.net",
        ksc_admin_user="KLAdmins"
    )


@patch("automation.python.remote.paramiko.SSHClient")
def test_connect_ksc_host(mock_ssh_class, dummy_config):
    mock_client = MagicMock()
    mock_ssh_class.return_value = mock_client

    client = connect_ksc_host(
        host=dummy_config.ksc_host,
        user=dummy_config.ksc_user,
        password=dummy_config.ksc_pass
    )

    assert client == mock_client
    mock_client.connect.assert_called_once_with(
        hostname=dummy_config.ksc_host,
        username=dummy_config.ksc_user,
        password=dummy_config.ksc_pass,
        timeout=15
    )


def test_run_remote_sudo():
    mock_client = MagicMock()
    mock_stdin = MagicMock()
    mock_stdout = MagicMock()
    mock_stderr = MagicMock()

    mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
    mock_stdout.read.return_value = b"root\n"
    mock_stderr.read.return_value = b""
    mock_stdout.channel.recv_exit_status.return_value = 0

    out, err, status = run_remote_sudo(mock_client, "whoami", "secretpass", stdin_inputs=["input1", "input2"])

    assert out == "root"
    assert err == ""
    assert status == 0
    mock_client.exec_command.assert_called_once_with("sudo -S whoami")
    mock_stdin.write.assert_any_call("secretpass\n")
    mock_stdin.write.assert_any_call("input1\n")
    mock_stdin.write.assert_any_call("input2\n")


def test_run_remote_sudo_batch():
    mock_client = MagicMock()
    mock_stdin = MagicMock()
    mock_stdout = MagicMock()
    mock_stderr = MagicMock()

    mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
    mock_stdout.read.return_value = b"success output"
    mock_stderr.read.return_value = b"some warning\n__KSC_FAIL__:1\nanother line"
    mock_stdout.channel.recv_exit_status.return_value = 1

    status, out, err, failed_indices = run_remote_sudo_batch(
        mock_client,
        ["cmd0", "cmd1", "cmd2"],
        "secretpass"
    )

    assert status == 1
    assert out == "success output"
    assert "some warning" in err
    assert failed_indices == [1]
    mock_stdin.write.assert_called_once_with("secretpass\n")
