import pytest
from unittest.mock import patch, MagicMock
from automation.ops.reconfigure_ksc_service import reconfigure_ksc_service
from automation.ops.purge_iam_mfa import OpsError


@patch("automation.ops.reconfigure_ksc_service.connect_ksc_host")
@patch("automation.ops.reconfigure_ksc_service.run_remote_sudo")
def test_reconfigure_ksc_service_uses_dynamic_temp_file_and_cleans_up(
    mock_run_remote_sudo, mock_connect
):
    dummy_config = MagicMock()
    dummy_config.ksc_host = "10.0.0.1"
    dummy_config.ksc_user = "admin"
    dummy_config.ksc_pass = "secret"
    dummy_config.ksc_fqdn = "ksc.local"
    dummy_config.db_password = "dbpass"
    dummy_config.ksc_admin_user = "admin"
    dummy_config.ksc_admin_password = "adminpass"

    mock_client = MagicMock()
    mock_sftp = MagicMock()
    mock_file = MagicMock()
    mock_sftp.file.return_value = mock_file
    mock_client.open_sftp.return_value = mock_sftp
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("stdout", "", 0)

    reconfigure_ksc_service(dummy_config, apply=True)

    # Verifica que o arquivo criado não é /tmp/reconfig_ans.txt fixo
    assert mock_sftp.file.called
    filename_arg = mock_sftp.file.call_args[0][0]
    assert filename_arg.startswith("/tmp/reconfig_ans_")
    assert filename_arg.endswith(".txt")
    assert filename_arg != "/tmp/reconfig_ans.txt"

    # Verifica que chmod(0o600) foi chamado
    mock_file.chmod.assert_called_once_with(0o600)

    # Verifica que rm -f foi chamado com o mesmo arquivo
    mock_client.exec_command.assert_any_call(f"rm -f {filename_arg}")


@patch("automation.ops.reconfigure_ksc_service.connect_ksc_host")
@patch("automation.ops.reconfigure_ksc_service.run_remote_sudo")
def test_reconfigure_ksc_service_cleans_up_on_error(
    mock_run_remote_sudo, mock_connect
):
    dummy_config = MagicMock()
    dummy_config.ksc_host = "10.0.0.1"
    dummy_config.ksc_user = "admin"
    dummy_config.ksc_pass = "secret"
    dummy_config.ksc_fqdn = "ksc.local"
    dummy_config.db_password = "dbpass"
    dummy_config.ksc_admin_user = "admin"
    dummy_config.ksc_admin_password = "adminpass"

    mock_client = MagicMock()
    mock_sftp = MagicMock()
    mock_file = MagicMock()
    mock_sftp.file.return_value = mock_file
    mock_client.open_sftp.return_value = mock_sftp
    mock_connect.return_value = mock_client
    # Simula erro no postinstall.pl
    mock_run_remote_sudo.return_value = ("", "Erro crítico no postinstall", 1)

    with pytest.raises(OpsError):
        reconfigure_ksc_service(dummy_config, apply=True)

    filename_arg = mock_sftp.file.call_args[0][0]
    mock_client.exec_command.assert_any_call(f"rm -f {filename_arg}")
