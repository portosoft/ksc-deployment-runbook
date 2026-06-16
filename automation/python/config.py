import logging
import os
import re
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ValidationError


class KscConfig(BaseModel):
    db_host: str = "127.0.0.1"
    db_port: int = Field(default=5432, ge=1, le=65535)
    db_name: str = "ksciam"
    db_user: str = "kluser"
    db_password: str
    db_sslmode: Literal["disable", "prefer", "require", "verify-ca", "verify-full"] = (
        "prefer"
    )
    ksc_admin_password: str
    ksc_license_path: Optional[str] = None
    web_port: int = Field(default=443, ge=1, le=65535)
    selinux_expected_mode: str = "enforcing"

    ksc_host: str = "127.0.0.1"
    ksc_user: str = "suporte"
    ksc_pass: Optional[str] = None
    ksc_fqdn: str = "ksc-placeholder.test"
    ksc_admin_user: str = "KLAdmins"

    @field_validator("ksc_fqdn")
    @classmethod
    def validate_fqdn(cls, v: str) -> str:
        # Expressão regular simples para FQDN, hostname ou IP (com (?i) no início)
        fqdn_regex = r"(?i)^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$|^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        if not re.match(fqdn_regex, v):
            raise ValueError(f"FQDN/Host inválido: {v}")
        return v

    @field_validator("ksc_admin_user")
    @classmethod
    def validate_admin_user(cls, v: str) -> str:
        # Whitelist de caracteres seguros
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(f"Nome de usuário administrativo inválido: {v}")
        return v


class ConfigError(Exception):
    pass


def _load_dotenv(path):
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
    Lê o .env, valida obrigatórios e retorna KscConfig usando Pydantic.
    Lança ConfigError em caso de problema.
    """
    if not os.path.exists(env_path):
        raise ConfigError(f"Arquivo de ambiente não encontrado: {env_path}")

    _load_dotenv(env_path)

    secrets_path = "configs/secrets.bin"  # pragma: allowlist secret
    if os.path.exists(secrets_path):
        try:
            from automation.lib.vault import decrypt_secrets
            vault_values = decrypt_secrets()
            for key, val in vault_values.items():
                os.environ[key] = val
        except Exception as exc:
            logging.warning("Vault decrypt falhou, usando .env: %s", exc)

    try:
        db_host = os.getenv("KSC_DB_HOST", "127.0.0.1")

        try:
            db_port = int(os.getenv("KSC_DB_PORT", "5432"))
        except ValueError:
            raise ConfigError(
                "Erro de conversão de tipo nas configurações: KSC_DB_PORT deve ser um inteiro"
            )

        db_name = os.getenv("KSC_IAM_NAME", "ksciam")
        db_user = os.getenv("KSC_DB_USER", "kluser")
        db_password = os.getenv("KSC_DB_PASS")
        db_sslmode = os.getenv("KSC_DB_SSLMODE", "prefer")
        ksc_admin_password = os.getenv("KSC_ADMIN_PASS")
        ksc_license_path = os.getenv("KSC_LICENSE_PATH")

        try:
            web_port = int(os.getenv("KSC_WEB_PORT", "443"))
        except ValueError:
            raise ConfigError(
                "Erro de conversão de tipo nas configurações: KSC_WEB_PORT deve ser um inteiro"
            )

        selinux_expected_mode = os.getenv("KSC_SELINUX_MODE", "enforcing")

        ksc_host = os.getenv("KSC_HOST", "127.0.0.1")
        ksc_user = os.getenv("KSC_USER", "suporte")
        ksc_pass = os.getenv("KSC_PASS")
        ksc_fqdn = os.getenv("KSC_FQDN", "ksc-placeholder.test")
        ksc_admin_user = os.getenv("KSC_ADMIN_USER", "KLAdmins")

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
            ksc_host=ksc_host,
            ksc_user=ksc_user,
            ksc_pass=ksc_pass,
            ksc_fqdn=ksc_fqdn,
            ksc_admin_user=ksc_admin_user,
        )
    except ValidationError as e:
        errors = []
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            errors.append(f"{loc}: {err['msg']}")
        raise ConfigError("Erro de validação nas configurações: " + "; ".join(errors))
