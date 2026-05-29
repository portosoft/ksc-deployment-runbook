import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class KscConfig:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_sslmode: str
    ksc_admin_password: str
    ksc_license_path: Optional[str]
    web_port: int
    selinux_expected_mode: str


class ConfigError(Exception):
    pass


def _load_dotenv(path):
    import os

    try:
        with open(path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v.strip("\"'")
    except Exception:
        pass


def load_config(env_path: str = "configs/env/ksc_vars.env") -> KscConfig:
    """
    Lê o .env, valida obrigatórios e retorna KscConfig.
    Lança ConfigError em caso de problema.
    """
    if not os.path.exists(env_path):
        raise ConfigError(f"Arquivo de ambiente não encontrado: {env_path}")

    _load_dotenv(env_path)

    try:
        # Puxamos as variáveis com prefixo KSC_ que costumam ser padrão
        db_host = os.getenv("KSC_DB_HOST", "127.0.0.1")
        db_port = int(os.getenv("KSC_DB_PORT", "5432"))
        db_name = os.getenv("KSC_IAM_NAME", "ksciam")
        db_user = os.getenv("KSC_DB_USER", "kluser")
        db_password = os.getenv("KSC_DB_PASS")
        db_sslmode = os.getenv("KSC_DB_SSLMODE", "prefer")
        ksc_admin_password = os.getenv("KSC_ADMIN_PASS")
        ksc_license_path = os.getenv("KSC_LICENSE_PATH")
        web_port = int(os.getenv("KSC_WEB_PORT", "443"))
        selinux_expected_mode = os.getenv("KSC_SELINUX_MODE", "enforcing")

        if not db_password:
            raise ConfigError("KSC_DB_PASS é obrigatória")
        if not ksc_admin_password:
            raise ConfigError("KSC_ADMIN_PASS é obrigatória")

        return KscConfig(
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            db_sslmode=db_sslmode,
            ksc_admin_password=ksc_admin_password,
            ksc_license_path=ksc_license_path,
            web_port=web_port,
            selinux_expected_mode=selinux_expected_mode,
        )
    except ValueError as e:
        raise ConfigError(f"Erro de conversão de tipo nas configurações: {e}")
