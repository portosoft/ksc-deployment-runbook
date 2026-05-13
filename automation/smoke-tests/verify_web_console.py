#!/usr/bin/env python3
import requests
import urllib3
import sys
import os
from dotenv import load_dotenv

# Desativar avisos de certificado auto-assinado para o teste inicial
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def smoke_test(url):
    print(f"--- Iniciando Smoke Test em {url} ---")
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            print("✅ SUCESSO: Web Console acessível (HTTP 200)")
            return True
        else:
            print(f"❌ FALHA: Web Console retornou Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERRO: Não foi possível conectar ao Web Console: {e}")
        return False

if __name__ == "__main__":
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv('KSC_HOST')
    port = os.getenv('KSC_WEB_PORT', '443')

    if not host:
        print("Erro: KSC_HOST não definido no .env")
        sys.exit(1)

    target_url = f"https://{host}:{port}/"
    if smoke_test(target_url):
        sys.exit(0)
    else:
        sys.exit(3)
