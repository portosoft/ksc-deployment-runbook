"""
tests/test_init_config.py — Testes de exemplo para automation/python/init_config.py

Cobre:
  - Fluxo feliz (happy path): sem arquivo existente, todos os campos preenchidos
  - Rejeição de sobrescrita: arquivo existe, operador recusa confirmação
  - Aceitação de sobrescrita: arquivo existe, operador confirma
  - Loop de re-prompt por FQDN inválido
  - Erro de I/O ao escrever o arquivo

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.9
"""
import sys
import pytest
from unittest.mock import MagicMock, patch, call

from automation.python import init_config
from automation.python.init_config import main
from automation.python.credentials import generate_password


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Non-sensitive field values (must align with NON_SENSITIVE_FIELDS order):
# KSC_DB_HOST, KSC_DB_PORT, KSC_DB_USER, KSC_FQDN, KSC_HOST,
# KSC_USER, KSC_WEB_PORT, KSC_SELINUX_MODE
_NON_SENSITIVE_VALUES = [
    "127.0.0.1",     # KSC_DB_HOST
    "5432",          # KSC_DB_PORT
    "kluser",        # KSC_DB_USER
    "ksc-abc12345.test",  # KSC_FQDN (valid synthetic FQDN)
    "127.0.0.1",     # KSC_HOST
    "suporte",       # KSC_USER
    "443",           # KSC_WEB_PORT
    "enforcing",     # KSC_SELINUX_MODE
]

# Sensitive field passwords — generated at module load, never hardcoded
_DB_PASS = generate_password()
_ADMIN_PASS = generate_password()
_KSC_PASS = generate_password()

_SENSITIVE_VALUES = [_DB_PASS, _ADMIN_PASS, _KSC_PASS]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHappyPath:
    """Test: no existing file, all fields entered, file written successfully.

    Validates: Requirements 5.1, 5.2, 5.5
    """

    def test_happy_path(self):
        mock_env_path = MagicMock()
        mock_env_path.exists.return_value = False
        mock_env_path.__str__ = lambda self: "configs/env/ksc_vars.env"

        with (
            patch.object(init_config, "ENV_FILE_PATH", mock_env_path),
            patch("builtins.input", side_effect=_NON_SENSITIVE_VALUES),
            patch("getpass.getpass", side_effect=_SENSITIVE_VALUES),
            patch("automation.python.init_config.write_secure_file") as mock_write,
            patch.object(sys, "argv", ["init_config"]),
        ):
            main()

        mock_write.assert_called_once()
        call_args = mock_write.call_args
        # First positional arg is the path
        written_path = call_args[0][0]
        # Second positional arg is the content
        written_content = call_args[0][1]

        assert "KSC_DB_HOST" in written_content
        assert "KSC_DB_PORT" in written_content
        assert "KSC_DB_USER" in written_content
        assert "KSC_FQDN" in written_content
        assert "KSC_HOST" in written_content
        assert "KSC_USER" in written_content
        assert "KSC_WEB_PORT" in written_content
        assert "KSC_SELINUX_MODE" in written_content
        assert "KSC_DB_PASS" in written_content
        assert "KSC_ADMIN_PASS" in written_content
        assert "KSC_PASS" in written_content


class TestOverwriteConfirmationRejected:
    """Test: file exists but operator declines overwrite → no write, exit 0.

    Validates: Requirements 5.4, 5.5
    """

    def test_overwrite_confirmation_rejected(self):
        mock_env_path = MagicMock()
        mock_env_path.exists.return_value = True
        mock_env_path.__str__ = lambda self: "configs/env/ksc_vars.env"

        with (
            patch.object(init_config, "ENV_FILE_PATH", mock_env_path),
            patch.object(init_config, "_parse_env_file", return_value={"KSC_DB_HOST": "old"}),
            patch("builtins.input", return_value="N"),
            patch("automation.python.init_config.write_secure_file") as mock_write,
            patch.object(sys, "argv", ["init_config"]),
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 0
        mock_write.assert_not_called()


class TestOverwriteConfirmationAccepted:
    """Test: file exists and operator confirms overwrite → file is written.

    Validates: Requirements 5.4, 5.5
    """

    def test_overwrite_confirmation_accepted(self):
        mock_env_path = MagicMock()
        mock_env_path.exists.return_value = True
        mock_env_path.__str__ = lambda self: "configs/env/ksc_vars.env"

        existing = {
            "KSC_DB_HOST": "10.0.0.1",
            "KSC_DB_PORT": "5432",
            "KSC_DB_USER": "kluser",
        }

        # input side_effect:
        #   first call: confirmation prompt → "s"
        #   then: one call per non-sensitive field (8 fields)
        input_values = ["s"] + _NON_SENSITIVE_VALUES

        with (
            patch.object(init_config, "ENV_FILE_PATH", mock_env_path),
            patch.object(init_config, "_parse_env_file", return_value=existing),
            patch("builtins.input", side_effect=input_values),
            patch("getpass.getpass", side_effect=_SENSITIVE_VALUES),
            patch("automation.python.init_config.write_secure_file") as mock_write,
            patch.object(sys, "argv", ["init_config"]),
        ):
            main()

        mock_write.assert_called_once()


class TestInvalidFqdnReprompt:
    """Test: invalid FQDN on first pass triggers re-prompt loop.

    Validates: Requirements 5.1, 5.3
    """

    def test_invalid_fqdn_reprompt(self):
        mock_env_path = MagicMock()
        mock_env_path.exists.return_value = False
        mock_env_path.__str__ = lambda self: "configs/env/ksc_vars.env"

        # First round: invalid FQDN at position 3 (KSC_FQDN)
        first_round = [
            "127.0.0.1",          # KSC_DB_HOST
            "5432",               # KSC_DB_PORT
            "kluser",             # KSC_DB_USER
            "invalid@host.com",   # KSC_FQDN — invalid, triggers validation failure
            "127.0.0.1",          # KSC_HOST
            "suporte",            # KSC_USER
            "443",                # KSC_WEB_PORT
            "enforcing",          # KSC_SELINUX_MODE
        ]
        # Second round: all valid including a valid FQDN
        second_round = _NON_SENSITIVE_VALUES[:]

        # Sensitive fields provided twice (once per outer loop iteration)
        sensitive_twice = _SENSITIVE_VALUES + _SENSITIVE_VALUES

        with (
            patch.object(init_config, "ENV_FILE_PATH", mock_env_path),
            patch("builtins.input", side_effect=first_round + second_round),
            patch("getpass.getpass", side_effect=sensitive_twice),
            patch("automation.python.init_config.write_secure_file") as mock_write,
            patch.object(sys, "argv", ["init_config"]),
        ):
            main()

        # Despite the re-prompt loop, write_secure_file is called exactly once
        mock_write.assert_called_once()
        written_content = mock_write.call_args[0][1]
        assert "KSC_FQDN=ksc-abc12345.test" in written_content


class TestIOErrorOnWrite:
    """Test: OSError during write exits with code 1.

    Validates: Requirement 5.9
    """

    def test_io_error_on_write(self):
        mock_env_path = MagicMock()
        mock_env_path.exists.return_value = False
        mock_env_path.__str__ = lambda self: "configs/env/ksc_vars.env"

        with (
            patch.object(init_config, "ENV_FILE_PATH", mock_env_path),
            patch("builtins.input", side_effect=_NON_SENSITIVE_VALUES),
            patch("getpass.getpass", side_effect=_SENSITIVE_VALUES),
            patch(
                "automation.python.init_config.write_secure_file",
                side_effect=OSError("permission denied"),
            ),
            patch.object(sys, "argv", ["init_config"]),
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1
