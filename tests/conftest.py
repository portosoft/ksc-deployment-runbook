"""
tests/conftest.py — Fixtures pytest para credenciais sintéticas e ambientes de arquivo temporário.

Importa exclusivamente:
  - automation.python.credentials (Credential_Generator)
  - automation.python.config (KscConfig)
  - automation.python.utils.secure_file (write_secure_file)

Nenhuma credencial literal é inserida neste arquivo.
"""
import pathlib

import pytest

from automation.python.credentials import (
    generate_password,
    generate_hostile_password,
    generate_test_db_name,
    generate_username,
)
from automation.python.config import KscConfig
from automation.python.utils.secure_file import write_secure_file


@pytest.fixture
def random_password() -> str:
    """Retorna o resultado de generate_password() — escopo function garante unicidade por teste."""
    return generate_password()


@pytest.fixture
def hostile_password() -> str:
    """Retorna o resultado de generate_hostile_password() — contém os cinco conjuntos obrigatórios."""
    return generate_hostile_password()


@pytest.fixture
def ksc_test_config() -> KscConfig:
    """Retorna KscConfig com valores sintéticos seguros para uso em testes unitários.

    Campos fixos permitidos para testes:
      db_host="127.0.0.1", db_port=5432

    Campos sensíveis gerados sinteticamente:
      db_password, ksc_admin_password — via generate_password()
      db_name — via generate_test_db_name()
      db_user — via generate_username()
    """
    return KscConfig(
        db_host="127.0.0.1",
        db_port=5432,
        db_password=generate_password(),
        ksc_admin_password=generate_password(),
        db_name=generate_test_db_name(),
        db_user=generate_username(),
    )


@pytest.fixture
def ksc_test_env_file(tmp_path) -> pathlib.Path:
    """Cria um arquivo .env sintético em tmp_path com permissão 0o600.

    O arquivo contém as chaves:
      KSC_DB_HOST, KSC_DB_PORT, KSC_IAM_NAME, KSC_DB_USER,
      KSC_DB_PASS, KSC_ADMIN_PASS, KSC_WEB_PORT

    Retorna o caminho do arquivo criado como pathlib.Path.
    """
    env_path = tmp_path / ".env"

    content = "\n".join([
        "KSC_DB_HOST=127.0.0.1",
        "KSC_DB_PORT=5432",
        f"KSC_IAM_NAME={generate_test_db_name()}",
        f"KSC_DB_USER={generate_username()}",
        f"KSC_DB_PASS={generate_password()}",
        f"KSC_ADMIN_PASS={generate_password()}",
        "KSC_WEB_PORT=443",
    ]) + "\n"

    write_secure_file(str(env_path), content, mode=0o600)

    return env_path
