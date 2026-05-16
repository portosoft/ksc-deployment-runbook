import os
import pytest
from unittest.mock import patch
from automation.python.config import KscConfig, ConfigError, load_config

def test_load_config_missing_file():
    with pytest.raises(ConfigError, match="Arquivo de ambiente não encontrado"):
        load_config("non_existent_env_file.env")

@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config.load_dotenv")
@patch.dict(os.environ, {"KSC_DB_PASS": "testpass", "KSC_ADMIN_PASS": "adminpass"})
def test_load_config_success(mock_load_dotenv, mock_exists):
    config = load_config("mock_path.env")
    assert isinstance(config, KscConfig)
    assert config.db_password == "testpass"
    assert config.ksc_admin_password == "adminpass"
    assert config.db_host == "127.0.0.1" # default

@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config.load_dotenv")
@patch.dict(os.environ, {"KSC_ADMIN_PASS": "adminpass"}, clear=True)
def test_load_config_missing_db_pass(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="KSC_DB_PASS é obrigatória"):
        load_config("mock_path.env")

@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config.load_dotenv")
@patch.dict(os.environ, {"KSC_DB_PASS": "testpass"}, clear=True)
def test_load_config_missing_admin_pass(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="KSC_ADMIN_PASS é obrigatória"):
        load_config("mock_path.env")

@patch("automation.python.config.os.path.exists", return_value=True)
@patch("automation.python.config.load_dotenv")
@patch.dict(os.environ, {"KSC_DB_PASS": "testpass", "KSC_ADMIN_PASS": "adminpass", "KSC_DB_PORT": "not_an_int"})
def test_load_config_invalid_type(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de conversão de tipo"):
        load_config("mock_path.env")
