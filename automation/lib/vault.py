from cryptography.fernet import Fernet
import os
import json

KEY_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../configs/vault.key")
)
SECRETS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../configs/secrets.bin")
)


def ensure_key():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
    with open(KEY_PATH, "rb") as f:
        return f.read()


def encrypt_secrets(secrets_dict):
    key = ensure_key()
    f = Fernet(key)
    data = json.dumps(secrets_dict).encode()
    encrypted = f.encrypt(data)
    with open(SECRETS_PATH, "wb") as f_out:
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
