import json
from unittest.mock import MagicMock, patch

import pytest

from automation.ops.fix_web_console_config import fix_web_console_config
from automation.ops.purge_iam_mfa import OpsError


@pytest.fixture
def sample_web_config():
    return {
        "port": "$web_console_port$",
        "address": "$web_console_address$",
        "openAPIServers": [
            {"address": "127.0.0.1", "port": "13000"}
        ],
    }


@patch("automation.ops.fix_web_console_config.connect_ksc_host")
@patch("automation.ops.fix_web_console_config.run_remote_sudo")
def test_fix_web_console_config_check_only(mock_run_remote_sudo, mock_connect, ksc_test_config):
    """Garante que no modo check-only nenhuma conexão SSH ou comando remoto seja executado."""
    fix_web_console_config(ksc_test_config, apply=False)

    mock_connect.assert_not_called()
    mock_run_remote_sudo.assert_not_called()


@patch("automation.ops.fix_web_console_config.connect_ksc_host")
@patch("automation.ops.fix_web_console_config.run_remote_sudo")
@patch("automation.ops.fix_web_console_config.write_secure_file")
def test_fix_web_console_config_updates_json_and_port_dynamically(
    mock_write_secure, mock_run_remote_sudo, mock_connect, ksc_test_config, sample_web_config
):
    """Garante que o config.json é atualizado via JSON nativo e porta dinâmica config.web_port."""
    ksc_test_config.web_port = 8443
    ksc_test_config.ksc_fqdn = "ksc.corp.internal"

    mock_client = MagicMock()
    mock_sftp = MagicMock()
    mock_file = MagicMock()
    mock_sftp.file.return_value = mock_file
    mock_client.open_sftp.return_value = mock_sftp
    mock_connect.return_value = mock_client

    # Simula leitura do config.json remoto via cat
    mock_run_remote_sudo.return_value = (json.dumps(sample_web_config), "", 0)

    fix_web_console_config(ksc_test_config, apply=True)

    # 1. Verifica que sed NÃO foi executado
    for call in mock_run_remote_sudo.call_args_list:
        cmd = call[0][1]
        assert "sed " not in cmd

    # 2. Verifica que write_secure_file foi chamado para gravação atômica
    assert mock_write_secure.called
    written_content = mock_write_secure.call_args[0][1]
    parsed_json = json.loads(written_content)

    assert parsed_json["port"] == 8443
    assert parsed_json["address"] == "ksc.corp.internal"
    assert parsed_json["openAPIServers"][0]["port"] == "13299"

    # 3. Verifica restart do serviço e fechamento do cliente
    assert any("systemctl restart ksc-web-console" in str(call) for call in mock_run_remote_sudo.call_args_list)
    mock_client.close.assert_called_once()


@patch("automation.ops.fix_web_console_config.connect_ksc_host")
@patch("automation.ops.fix_web_console_config.run_remote_sudo")
def test_fix_web_console_config_read_failure_raises_ops_error(
    mock_run_remote_sudo, mock_connect, ksc_test_config
):
    """Garante que falha na leitura remota do config.json dispara OpsError."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("", "cat: config.json: No such file or directory", 1)

    with pytest.raises(OpsError, match="Falha ao ler"):
        fix_web_console_config(ksc_test_config, apply=True)

    mock_client.close.assert_called_once()


@patch("automation.ops.fix_web_console_config.connect_ksc_host")
@patch("automation.ops.fix_web_console_config.run_remote_sudo")
def test_fix_web_console_config_invalid_json_raises_ops_error(
    mock_run_remote_sudo, mock_connect, ksc_test_config
):
    """Garante que conteúdo JSON corrompido ou inválido dispara OpsError."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("{ invalid json syntax ...", "", 0)

    with pytest.raises(OpsError, match="Falha ao interpretar JSON"):
        fix_web_console_config(ksc_test_config, apply=True)

    mock_client.close.assert_called_once()


@patch("automation.ops.fix_web_console_config.connect_ksc_host")
@patch("automation.ops.fix_web_console_config.run_remote_sudo")
def test_fix_web_console_config_restart_failure_raises_ops_error(
    mock_run_remote_sudo, mock_connect, ksc_test_config, sample_web_config
):
    """Garante que falha no restart do serviço ksc-web-console dispara OpsError."""
    mock_client = MagicMock()
    mock_sftp = MagicMock()
    mock_client.open_sftp.return_value = mock_sftp
    mock_connect.return_value = mock_client

    # cat ok, mv/chown ok, restart falha
    mock_run_remote_sudo.side_effect = [
        (json.dumps(sample_web_config), "", 0),
        ("", "", 0),  # mv
        ("", "", 0),  # chown
        ("", "Job for ksc-web-console.service failed", 1),  # restart
    ]

    with pytest.raises(OpsError, match="Falha ao reiniciar o serviço ksc-web-console"):
        fix_web_console_config(ksc_test_config, apply=True)

    mock_client.close.assert_called_once()


@patch("automation.ops.fix_web_console_config.connect_ksc_host")
@patch("automation.ops.fix_web_console_config.run_remote_sudo")
def test_fix_web_console_config_client_closed_in_finally(
    mock_run_remote_sudo, mock_connect, ksc_test_config
):
    """Garante que client.close() é chamado sob qualquer falha."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.side_effect = RuntimeError("Erro SSH")

    with pytest.raises(OpsError):
        fix_web_console_config(ksc_test_config, apply=True)

    mock_client.close.assert_called_once()
