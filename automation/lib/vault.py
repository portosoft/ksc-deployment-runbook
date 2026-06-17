from cryptography.fernet import Fernet
import os
import json
import stat

KEY_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../configs/vault.key")
)
SECRETS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../configs/secrets.bin")
)


def _assert_secure(path: str, required_mode: int = 0o600) -> None:
    """Verifica se o arquivo possui permissões restritas (padrão 0o600).

    Levanta PermissionError se o arquivo estiver com permissões mais permissivas.
    """
    mode = os.stat(path).st_mode & 0o777
    if mode != required_mode:
        raise PermissionError(
            f"Arquivo {path} tem permissão {oct(mode)}, esperado {oct(required_mode)}. "
            "Execute: chmod {req} {path}".format(req=oct(required_mode), path=path)
        )


def ensure_key():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        # 🛡️ Sentinel: Enforce strict permissions (0o600) on vault key creation
        with os.fdopen(os.open(KEY_PATH, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600), "wb") as f:
            f.write(key)
    # 🛡️ Sentinel: Verify existing key file permissions before reading
    _assert_secure(KEY_PATH, 0o600)
    with open(KEY_PATH, "rb") as f:
        return f.read()


def encrypt_secrets(secrets_dict):
    key = ensure_key()
    f = Fernet(key)
    data = json.dumps(secrets_dict).encode()
    encrypted = f.encrypt(data)
    # 🛡️ Sentinel: Enforce strict permissions (0o600) on encrypted secrets file creation
    with os.fdopen(os.open(SECRETS_PATH, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600), "wb") as f_out:
        f_out.write(encrypted)


def decrypt_secrets():
    if not os.path.exists(SECRETS_PATH):
        return {}
    key = ensure_key()
    f = Fernet(key)
    with open(SECRETS_PATH, "rb") as f_in:
        encrypted = f_in.read()
    data = f.decrypt(encrypted)
    return json.loads(data.decode())
