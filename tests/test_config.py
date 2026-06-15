import os
import pytest
from unittest.mock import patch
from automation.python.config import KscConfig, ConfigError, load_config


def test_load_config_missing_file():
    with pytest.raises(ConfigError, match="Arquivo de ambiente não encontrado"):
        load_config("non_existent_env_file.env")


@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config._load_dotenv")
@patch.dict(os.environ, {"KSC_DB_PASS": "unittest-dummy-db-pass-000", "KSC_ADMIN_PASS": "unittest-dummy-admin-pass-999"})  # pragma: allowlist secret
def test_load_config_success(mock_load_dotenv, mock_exists):
    config = load_config("mock_path.env")
    assert isinstance(config, KscConfig)
    assert config.db_password == "unittest-dummy-db-pass-000"  # pragma: allowlist secret
    assert config.ksc_admin_password == "unittest-dummy-admin-pass-999"  # pragma: allowlist secret
    assert config.db_host == "127.0.0.1"  # default


@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config._load_dotenv")
@patch.dict(os.environ, {"KSC_ADMIN_PASS": "unittest-dummy-admin-pass-999"}, clear=True)  # pragma: allowlist secret
def test_load_config_missing_db_pass(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="KSC_DB_PASS é obrigatória"):
        load_config("mock_path.env")


@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config._load_dotenv")
@patch.dict(os.environ, {"KSC_DB_PASS": "unittest-dummy-db-pass-000"}, clear=True)  # pragma: allowlist secret
def test_load_config_missing_admin_pass(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="KSC_ADMIN_PASS é obrigatória"):
        load_config("mock_path.env")


@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": "unittest-dummy-db-pass-000",  # pragma: allowlist secret
        "KSC_ADMIN_PASS": "unittest-dummy-admin-pass-999",  # pragma: allowlist secret
        "KSC_DB_PORT": "not_an_int",
    },
)
def test_load_config_invalid_type(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de conversão de tipo"):
        load_config("mock_path.env")


@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": "unittest-dummy-db-pass-000",  # pragma: allowlist secret
        "KSC_ADMIN_PASS": "unittest-dummy-admin-pass-999",  # pragma: allowlist secret
        "KSC_FQDN": "invalid@fqdn.com",
    },
)
def test_load_config_invalid_fqdn(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de validação nas configurações.*fqdn"):
        load_config("mock_path.env")


@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": "unittest-dummy-db-pass-000",  # pragma: allowlist secret
        "KSC_ADMIN_PASS": "unittest-dummy-admin-pass-999",  # pragma: allowlist secret
        "KSC_ADMIN_USER": "admin; injection",
    },
)
def test_load_config_invalid_admin_user(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de validação nas configurações.*admin_user"):
        load_config("mock_path.env")


@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": "unittest-dummy-db-pass-000",  # pragma: allowlist secret
        "KSC_ADMIN_PASS": "unittest-dummy-admin-pass-999",  # pragma: allowlist secret
        "KSC_DB_PORT": "70000",
    },
)
def test_load_config_invalid_port_range(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de validação nas configurações.*db_port"):
        load_config("mock_path.env")


@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": "unittest-dummy-db-pass-000",  # pragma: allowlist secret
        "KSC_ADMIN_PASS": "unittest-dummy-admin-pass-999",  # pragma: allowlist secret
        "KSC_DB_SSLMODE": "invalid-ssl-mode",
    },
)
def test_load_config_invalid_sslmode(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de validação nas configurações.*db_sslmode"):
        load_config("mock_path.env")
