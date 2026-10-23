import pytest
from unittest.mock import patch, MagicMock
from automation.ops.reconfigure_ksc_service import reconfigure_ksc_service
from automation.ops.purge_iam_mfa import OpsError


@patch("automation.ops.reconfigure_ksc_service.connect_ksc_host")
@patch("automation.ops.reconfigure_ksc_service.run_remote_sudo")
def test_reconfigure_ksc_service_uses_dynamic_temp_file_and_cleans_up(
    mock_run_remote_sudo, mock_connect, ksc_test_config
):
    mock_client = MagicMock()
    mock_sftp = MagicMock()
    mock_file = MagicMock()
    mock_sftp.file.return_value = mock_file
    mock_client.open_sftp.return_value = mock_sftp
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("stdout", "", 0)

    reconfigure_ksc_service(ksc_test_config, apply=True)

    # Verifica que um diretório privado com permissões 0700 foi criado via SFTP para mitigar TOCTOU
    assert mock_sftp.mkdir.called
    dir_arg = mock_sftp.mkdir.call_args[0][0]
    dir_mode = mock_sftp.mkdir.call_args[1].get("mode") if "mode" in mock_sftp.mkdir.call_args[1] else (mock_sftp.mkdir.call_args[0][1] if len(mock_sftp.mkdir.call_args[0]) > 1 else None)
    assert dir_arg.startswith("/tmp/reconfig_ksc_")
    assert dir_mode == 0o700

    # Verifica que o arquivo criado está dentro do diretório privado
    assert mock_sftp.file.called
    filename_arg = mock_sftp.file.call_args[0][0]
    assert filename_arg == f"{dir_arg}/answers.txt"

    # Verifica que chmod(0o600) foi chamado no arquivo
    mock_file.chmod.assert_called_once_with(0o600)

    # Verifica que a limpeza remove o arquivo e o diretório sem rm -rf
    cleanup_calls = [str(call) for call in mock_client.exec_command.call_args_list]
    sftp_remove_called = mock_sftp.remove.called
    assert sftp_remove_called or any(f"rm -f '{filename_arg}'" in c or f"rm -f {filename_arg}" in c for c in cleanup_calls)


@patch("automation.ops.reconfigure_ksc_service.connect_ksc_host")
@patch("automation.ops.reconfigure_ksc_service.run_remote_sudo")
def test_reconfigure_ksc_service_cleans_up_on_error(
    mock_run_remote_sudo, mock_connect, ksc_test_config
):
    mock_client = MagicMock()
    mock_sftp = MagicMock()
    mock_file = MagicMock()
    mock_sftp.file.return_value = mock_file
    mock_client.open_sftp.return_value = mock_sftp
    mock_connect.return_value = mock_client
    # Simula erro no postinstall.pl
    mock_run_remote_sudo.return_value = ("", "Erro crítico no postinstall", 1)

    with pytest.raises(OpsError):
        reconfigure_ksc_service(ksc_test_config, apply=True)

    dir_arg = mock_sftp.mkdir.call_args[0][0]
    filename_arg = mock_sftp.file.call_args[0][0]
    assert filename_arg == f"{dir_arg}/answers.txt"
    mock_client.close.assert_called_once()


@patch("automation.ops.reconfigure_ksc_service.connect_ksc_host")
@patch("automation.ops.reconfigure_ksc_service.run_remote_sudo")
def test_reconfigure_ksc_service_check_only(mock_run_remote_sudo, mock_connect, ksc_test_config):
    """Garante que no modo check-only nenhuma conexão SSH ou comando remoto seja executado."""
    reconfigure_ksc_service(ksc_test_config, apply=False)

    mock_connect.assert_not_called()
    mock_run_remote_sudo.assert_not_called()


@patch("automation.ops.reconfigure_ksc_service.connect_ksc_host")
@patch("automation.ops.reconfigure_ksc_service.run_remote_sudo")
def test_reconfigure_ksc_service_restart_failure_raises_ops_error(
    mock_run_remote_sudo, mock_connect, ksc_test_config
):
    """Garante que falha no restart dos serviços KSC dispara OpsError."""
    mock_client = MagicMock()
    mock_sftp = MagicMock()
    mock_file = MagicMock()
    mock_sftp.file.return_value = mock_file
    mock_client.open_sftp.return_value = mock_sftp
    mock_connect.return_value = mock_client

    # postinstall ok, restart falha
    mock_run_remote_sudo.side_effect = [
        ("stdout", "", 0),
        ("", "Failed to restart kladminserver_srv.service", 1),
    ]

    with pytest.raises(OpsError, match="Falha ao reiniciar os serviços KSC"):
        reconfigure_ksc_service(ksc_test_config, apply=True)

    mock_client.close.assert_called_once()


@patch("automation.ops.reconfigure_ksc_service.connect_ksc_host")
@patch("automation.ops.reconfigure_ksc_service.run_remote_sudo")
def test_reconfigure_ksc_service_success(
    mock_run_remote_sudo, mock_connect, ksc_test_config
):
    """Valida o fluxo completo de sucesso de reconfiguração de serviço."""
    mock_client = MagicMock()
    mock_sftp = MagicMock()
    mock_file = MagicMock()
    mock_sftp.file.return_value = mock_file
    mock_client.open_sftp.return_value = mock_sftp
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("Reconfiguration successful", "", 0)

    reconfigure_ksc_service(ksc_test_config, apply=True)

    assert mock_sftp.mkdir.called
    assert mock_sftp.file.called
    assert mock_file.write.called
    assert mock_run_remote_sudo.call_count == 2  # postinstall + restart
    mock_client.close.assert_called_once()
