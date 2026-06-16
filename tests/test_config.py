import logging
import os
import pytest
from unittest.mock import patch
from automation.python.config import KscConfig, ConfigError, load_config
from automation.python.credentials import generate_password

# Module-level passwords generated at import time — no hardcoded secrets
_DB_PASS = generate_password()
_ADMIN_PASS = generate_password()
_VAULT_PASS = generate_password()

_MOCK_ENV_PATH = "mock_path.env"
_SECRETS_PATH = "configs/secrets.bin"  # pragma: allowlist secret


def _exists_env_only(path: str) -> bool:
    return path == _MOCK_ENV_PATH


def _exists_env_and_secrets(path: str) -> bool:
    return path in (_MOCK_ENV_PATH, _SECRETS_PATH)


def test_load_config_missing_file():
    with pytest.raises(ConfigError, match="Arquivo de ambiente não encontrado"):
        load_config("non_existent_env_file.env")


@patch("automation.python.config.os.path.exists", side_effect=_exists_env_only)
@patch("automation.python.config._load_dotenv")
@patch.dict(os.environ, {"KSC_DB_PASS": _DB_PASS, "KSC_ADMIN_PASS": _ADMIN_PASS})
def test_load_config_success(mock_load_dotenv, mock_exists):
    config = load_config(_MOCK_ENV_PATH)
    assert isinstance(config, KscConfig)
    assert config.db_password == _DB_PASS
    assert config.ksc_admin_password == _ADMIN_PASS
    assert config.db_host == "127.0.0.1"  # default


@patch("automation.python.config.os.path.exists", side_effect=_exists_env_only)
@patch("automation.python.config._load_dotenv")
@patch.dict(os.environ, {"KSC_ADMIN_PASS": _ADMIN_PASS}, clear=True)
def test_load_config_missing_db_pass(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="KSC_DB_PASS é obrigatória"):
        load_config(_MOCK_ENV_PATH)


@patch("automation.python.config.os.path.exists", side_effect=_exists_env_only)
@patch("automation.python.config._load_dotenv")
@patch.dict(os.environ, {"KSC_DB_PASS": _DB_PASS}, clear=True)
def test_load_config_missing_admin_pass(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="KSC_ADMIN_PASS é obrigatória"):
        load_config(_MOCK_ENV_PATH)


@patch("automation.python.config.os.path.exists", side_effect=_exists_env_only)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": _DB_PASS,
        "KSC_ADMIN_PASS": _ADMIN_PASS,
        "KSC_DB_PORT": "not_an_int",
    },
)
def test_load_config_invalid_type(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de conversão de tipo"):
        load_config(_MOCK_ENV_PATH)


@patch("automation.python.config.os.path.exists", side_effect=_exists_env_only)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": _DB_PASS,
        "KSC_ADMIN_PASS": _ADMIN_PASS,
        "KSC_FQDN": "invalid@fqdn.com",
    },
)
def test_load_config_invalid_fqdn(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de validação nas configurações.*fqdn"):
        load_config(_MOCK_ENV_PATH)


@patch("automation.python.config.os.path.exists", side_effect=_exists_env_only)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": _DB_PASS,
        "KSC_ADMIN_PASS": _ADMIN_PASS,
        "KSC_ADMIN_USER": "admin; injection",
    },
)
def test_load_config_invalid_admin_user(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de validação nas configurações.*admin_user"):
        load_config(_MOCK_ENV_PATH)


@patch("automation.python.config.os.path.exists", side_effect=_exists_env_only)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": _DB_PASS,
        "KSC_ADMIN_PASS": _ADMIN_PASS,
        "KSC_DB_PORT": "70000",
    },
)
def test_load_config_invalid_port_range(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de validação nas configurações.*db_port"):
        load_config(_MOCK_ENV_PATH)


@patch("automation.python.config.os.path.exists", side_effect=_exists_env_only)
@patch("automation.python.config._load_dotenv")
@patch.dict(
    os.environ,
    {
        "KSC_DB_PASS": _DB_PASS,
        "KSC_ADMIN_PASS": _ADMIN_PASS,
        "KSC_DB_SSLMODE": "invalid-ssl-mode",
    },
)
def test_load_config_invalid_sslmode(mock_load_dotenv, mock_exists):
    with pytest.raises(ConfigError, match="Erro de validação nas configurações.*db_sslmode"):
        load_config(_MOCK_ENV_PATH)


# --- Vault integration tests (Requirements 6.3, 6.4) ---

@patch("automation.lib.vault.decrypt_secrets", return_value={"KSC_DB_PASS": _VAULT_PASS})
@patch("automation.python.config.os.path.exists", side_effect=_exists_env_and_secrets)
@patch("automation.python.config._load_dotenv")
@patch.dict(os.environ, {"KSC_DB_PASS": _DB_PASS, "KSC_ADMIN_PASS": _ADMIN_PASS})
def test_load_config_vault_merges_over_env(mock_load_dotenv, mock_exists, mock_decrypt):
    """Vault values override .env values (Requirement 6.3)."""
    config = load_config(_MOCK_ENV_PATH)
    assert config.db_password == _VAULT_PASS


@patch("automation.lib.vault.decrypt_secrets", side_effect=Exception("vault error"))
@patch("automation.python.config.os.path.exists", side_effect=_exists_env_and_secrets)
@patch("automation.python.config._load_dotenv")
@patch.dict(os.environ, {"KSC_DB_PASS": _DB_PASS, "KSC_ADMIN_PASS": _ADMIN_PASS})
def test_load_config_vault_decrypt_failure_uses_env(mock_load_dotenv, mock_exists, mock_decrypt, caplog):
    """When vault decrypt raises, falls back to .env values and logs a WARNING (Requirement 6.4)."""
    with caplog.at_level(logging.WARNING):
        config = load_config(_MOCK_ENV_PATH)
    assert config.db_password == _DB_PASS
    assert any("vault" in record.message.lower() or "vault" in record.getMessage().lower()
               for record in caplog.records)
