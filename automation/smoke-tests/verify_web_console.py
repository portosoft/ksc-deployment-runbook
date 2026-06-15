# -*- coding: utf-8 -*-
"""
Smoke test para verificar a acessibilidade do Kaspersky Web Console.
"""

import sys
import argparse
import requests
import urllib3
from automation.python.config import load_config, ConfigError


def smoke_test(url: str, verify: bool = True) -> bool:
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

    if smoke_test(target_url, verify=verify):
        sys.exit(0)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main()
