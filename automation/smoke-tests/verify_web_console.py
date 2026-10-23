# -*- coding: utf-8 -*-
"""
Smoke test para verificar a acessibilidade do Kaspersky Web Console.
"""

import argparse
from pathlib import Path
import sys
import pytest
import requests
import urllib3

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from automation.python.config import ConfigError, load_config


def check_web_console_accessible(url: str, verify: bool = True) -> bool:
    print(f"--- Iniciando Smoke Test em {url} (verificação TLS: {verify}) ---")
    if not verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        response = requests.get(url, verify=verify, timeout=10)
        if response.status_code == 200:
            print("✅ SUCESSO: Web Console acessível (HTTP 200)")
            return True
        else:
            print(f"❌ FALHA: Web Console retornou Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERRO: Não foi possível conectar ao Web Console: {e}")
        return False


@pytest.mark.smoke
def test_smoke_web_console():
    """Smoke test: valida acessibilidade do Web Console do KSC."""
    try:
        config = load_config()
    except ConfigError as e:
        pytest.skip(f"Configuração KSC não disponível para smoke test: {e}")

    target_url = f"https://{config.ksc_host}:{config.web_port}/"
    success = check_web_console_accessible(target_url, verify=False)
    assert success, f"Web Console inacessível em {target_url}"


def main():
    parser = argparse.ArgumentParser(description="Smoke test para o Web Console do KSC")
    parser.add_argument(
        "--config",
        default="configs/env/ksc_vars.env",
        help="Caminho do arquivo de configuração",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Desabilita a verificação do certificado SSL (TLS) para testes iniciais",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except ConfigError as e:
        print(f"Erro ao carregar configurações: {e}")
        sys.exit(1)

    target_url = f"https://{config.ksc_host}:{config.web_port}/"
    verify = not args.insecure

    if not verify:
        print("⚠️ AVISO: A verificação de certificados SSL/TLS está desativada.")

    if check_web_console_accessible(target_url, verify=verify):
        sys.exit(0)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main()
