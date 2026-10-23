# -*- coding: utf-8 -*-
"""
Testes unitários para o módulo remote.py (conexão SSH e execução sudo remota).

Usa a fixture ksc_test_config do conftest.py para credenciais sintéticas,
sem valores literais hardcoded.
"""
from unittest.mock import MagicMock, patch
from automation.python.remote import connect_ksc_host, run_remote_sudo, run_remote_sudo_batch


@patch("automation.python.remote.paramiko.SSHClient")
def test_connect_ksc_host(mock_ssh_class, ksc_test_config):
    mock_client = MagicMock()
    mock_ssh_class.return_value = mock_client

    client = connect_ksc_host(
        host=ksc_test_config.ksc_host,
        user=ksc_test_config.ksc_user,
        password=ksc_test_config.ksc_pass
    )

    assert client == mock_client
    mock_client.load_system_host_keys.assert_called_once()
    assert mock_client.set_missing_host_key_policy.call_count == 1
    mock_client.connect.assert_called_once_with(
        hostname=ksc_test_config.ksc_host,
        username=ksc_test_config.ksc_user,
        password=ksc_test_config.ksc_pass,
        timeout=15
    )


@patch("automation.python.remote.paramiko.SSHClient")
def test_connect_ksc_host_unknown_host_error_guidance(mock_ssh_class, ksc_test_config, caplog):
    import paramiko
    import pytest

    mock_client = MagicMock()
    mock_ssh_class.return_value = mock_client
    mock_client.connect.side_effect = paramiko.SSHException("Server '192.168.1.50' not found in known_hosts")

    with caplog.at_level("ERROR"):
        with pytest.raises(paramiko.SSHException):
            connect_ksc_host(
                host=ksc_test_config.ksc_host,
                user=ksc_test_config.ksc_user,
                password=ksc_test_config.ksc_pass
            )

    assert "ssh-keyscan" in caplog.text
    assert "RejectPolicy" in caplog.text


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
