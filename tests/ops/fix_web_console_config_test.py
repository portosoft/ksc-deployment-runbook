import shlex
from unittest.mock import patch, MagicMock

from automation.ops.fix_web_console_config import fix_web_console_config


@patch("automation.ops.fix_web_console_config.connect_ksc_host")
@patch("automation.ops.fix_web_console_config.run_remote_sudo")
def test_fix_web_console_config_secure_quoting(
    mock_run_remote_sudo, mock_connect, ksc_test_config
):
    """
    Testa se o FQDN malicioso fornecido no config é corretamente escapado
    e se o comando sed gerado está protegido contra command injection.
    """
    ksc_test_config.ksc_fqdn = "ksc.test.local/malicious/string'; rm -rf /; '"

    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("stdout", "stderr", 0)

    fix_web_console_config(ksc_test_config, apply=True)

    assert mock_run_remote_sudo.called
    calls = mock_run_remote_sudo.call_args_list
    sed_call = calls[0]
    executed_cmd = sed_call[0][1]

    safe_fqdn = ksc_test_config.ksc_fqdn.replace("/", r"\/")
    expected_expr_addr = f's/\\$web_console_address\\$/{safe_fqdn}/g'

    assert shlex.quote(expected_expr_addr) in executed_cmd
