import pytest
import shlex

from unittest.mock import patch, MagicMock
from automation.ops.purge_iam_mfa import OpsError, purge_iam_mfa
from automation.python.config import KscConfig
from automation.python.credentials import (
    generate_password,
    generate_synthetic_fqdn,
    generate_username,
)


@pytest.fixture
def dummy_config():
    # Credenciais geradas em vez de literais: strings com aparência de senha no
    # código-fonte poluem o baseline de segredos com falsos positivos.
    return KscConfig(
        db_host="127.0.0.1",
        db_password=generate_password(),
        ksc_admin_password=generate_password(),
        ksc_host=generate_synthetic_fqdn(),
        ksc_user=generate_username(),
        ksc_pass=generate_password(),
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
        assert calls[i][0][2] == dummy_config.ksc_pass

    # Test the restart command
    assert (
        calls[3][0][1]
        == "systemctl restart kladminserver_srv kliam_srv ksc-web-console"
    )


@patch("automation.ops.purge_iam_mfa.connect_ksc_host")
@patch("automation.ops.purge_iam_mfa.run_remote_sudo")
def test_purge_iam_mfa_check_only(mock_run_remote_sudo, mock_connect, dummy_config):
    """Garante que no modo check-only nenhuma conexão SSH ou comando remoto seja executado."""
    purge_iam_mfa(dummy_config, apply=False)

    mock_connect.assert_not_called()
    mock_run_remote_sudo.assert_not_called()


@patch("automation.ops.purge_iam_mfa.connect_ksc_host")
@patch("automation.ops.purge_iam_mfa.run_remote_sudo")
def test_purge_iam_mfa_query_failure_raises_ops_error(mock_run_remote_sudo, mock_connect, dummy_config):
    """Garante que falha em query SQL remota dispara OpsError."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.return_value = ("", "psql error: relation does not exist", 1)

    with pytest.raises(OpsError, match="Falha ao executar query no Postgres"):
        purge_iam_mfa(dummy_config, apply=True)


@patch("automation.ops.purge_iam_mfa.connect_ksc_host")
@patch("automation.ops.purge_iam_mfa.run_remote_sudo")
def test_purge_iam_mfa_restart_failure_raises_ops_error(mock_run_remote_sudo, mock_connect, dummy_config):
    """Garante que falha ao reiniciar os serviços KSC dispara OpsError."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.side_effect = [
        ("stdout", "", 0),
        ("stdout", "", 0),
        ("stdout", "", 0),
        ("", "systemctl error: job failed", 1),
    ]

    with pytest.raises(OpsError, match="Falha ao reiniciar os serviços KSC"):
        purge_iam_mfa(dummy_config, apply=True)


@patch("automation.ops.purge_iam_mfa.connect_ksc_host")
@patch("automation.ops.purge_iam_mfa.run_remote_sudo")
def test_purge_iam_mfa_client_closed_in_finally(mock_run_remote_sudo, mock_connect, dummy_config):
    """Garante que client.close() é chamado mesmo quando uma exceção ocorre durante a execução."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_run_remote_sudo.side_effect = RuntimeError("Conexão SSH interrompida")

    with pytest.raises(OpsError):
        purge_iam_mfa(dummy_config, apply=True)

    mock_client.close.assert_called_once()
