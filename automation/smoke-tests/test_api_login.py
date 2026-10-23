# -*- coding: utf-8 -*-
"""
Smoke test para testar o login remoto no OpenAPI do KSC 16.x Linux.
"""

import argparse
import base64
from pathlib import Path
import ssl
import sys
import urllib.request
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from automation.python.config import ConfigError, load_config


def check_api_login(
    host: str, web_port: int, admin_user: str, admin_pass: str, verify: bool = True
) -> bool:
    server = f"https://{host}:13299"
    print(f"--- Testando OpenAPI Login em {server} (verificação TLS: {verify}) ---")

    if not verify:
        context = ssl._create_unverified_context()
    else:
        context = ssl.create_default_context()

    u64 = base64.b64encode(admin_user.encode()).decode()
    p64 = base64.b64encode(admin_pass.encode()).decode()

    # Cabeçalho exigido pelo KSC 16.x Linux
    auth_header = f'KSCBasic user="{u64}", pass="{p64}", internal="1"'
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(
        f"{server}/api/v1.0/login", data=b"{}", headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(req, context=context, timeout=10):
            print(f"✅ SUCCESS: Login bem-sucedido com usuário {admin_user}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"❌ FAILED: HTTP {e.code} - {body}")
        return False
    except Exception as e:
        print(f"❌ ERR: {e}")
        return False


@pytest.mark.smoke
def test_smoke_api_login():
    """Smoke test: valida login na OpenAPI remota do KSC 16.x."""
    try:
        config = load_config()
    except ConfigError as e:
        pytest.skip(f"Configuração KSC não disponível para smoke test: {e}")

    if not config.ksc_admin_password:
        pytest.skip("ksc_admin_password não configurada.")

    success = check_api_login(
        config.ksc_host,
        config.web_port,
        config.ksc_admin_user,
        config.ksc_admin_password,
        verify=False,
    )
    assert success, "Falha ao autenticar na OpenAPI do KSC"


def main():
    parser = argparse.ArgumentParser(
        description="Smoke test para login do OpenAPI no KSC"
    )
    parser.add_argument(
        "--config",
        default="configs/env/ksc_vars.env",
        help="Caminho do arquivo de configuração",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Desabilita a verificação do certificado SSL (TLS)",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except ConfigError as e:
        print(f"Erro ao carregar configurações: {e}")
        sys.exit(1)

    if not config.ksc_admin_password:
        print("Erro: ksc_admin_password não configurada.")
        sys.exit(1)

    verify = not args.insecure
    if not verify:
        print("⚠️ AVISO: A verificação de certificados SSL/TLS está desativada.")

    if check_api_login(
        config.ksc_host,
        config.web_port,
        config.ksc_admin_user,
        config.ksc_admin_password,
        verify=verify,
    ):
        sys.exit(0)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main()
