import pytest
import shlex
from unittest.mock import patch, MagicMock

from automation.python.config import KscConfig
from automation.ops.fix_web_console_config import fix_web_console_config

@patch("automation.ops.fix_web_console_config.connect_ksc_host")
@patch("automation.ops.fix_web_console_config.run_remote_sudo")
def test_fix_web_console_config_secure_quoting(
    mock_run_remote_sudo, mock_connect
):
    """
    Testa se o FQDN malicioso fornecido no config é corretamente escapado
    e se o comando sed gerado está protegido contra command injection.
    """
    # Create a mock config instead of instantiating KscConfig, to bypass validation
    dummy_config = MagicMock()
    dummy_config.ksc_host = "10.0.0.1"
    dummy_config.ksc_user = "admin"
    dummy_config.ksc_pass = "secret"
    dummy_config.ksc_fqdn = "ksc.test.local/malicious/string"

    # Configura o mock do connect_ksc_host
    mock_client = MagicMock()
    mock_connect.return_value = mock_client

    # Configura o mock do run_remote_sudo para simular sucesso
    mock_run_remote_sudo.return_value = ("stdout", "stderr", 0)

    # Executa a função no modo apply (para chamar o run_remote_sudo)
    fix_web_console_config(dummy_config, apply=True)

    # Verifica se o run_remote_sudo foi chamado
    assert mock_run_remote_sudo.called

    # Captura a primeira chamada que deve ser o sed
    calls = mock_run_remote_sudo.call_args_list
    sed_call = calls[0]

    # args são: (client, cmd, password)
    executed_cmd = sed_call[0][1]

    # Verifica se o FQDN malicioso teve suas barras escapadas
    # ksc.test.local/malicious/string -> ksc.test.local\/malicious\/string
    safe_fqdn = r"ksc.test.local\/malicious\/string"
    expected_expr_addr = f's/\\$web_console_address\\$/{safe_fqdn}/g'

    # Verifica se a expressão completa está citada corretamente usando shlex.quote
    assert shlex.quote(expected_expr_addr) in executed_cmd
