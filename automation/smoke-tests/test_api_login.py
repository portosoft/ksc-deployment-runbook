#!/usr/bin/env python3
import os
import sys
import urllib.request
import base64
import json
import ssl
from dotenv import load_dotenv

# Configuração
load_dotenv("configs/env/ksc_vars.env")
context = ssl._create_unverified_context()

SERVER = "https://127.0.0.1:13299"
ADMIN_USER = os.getenv('KSC_ADMIN_USER', 'KLAdmins')
ADMIN_PASS = os.getenv('KSC_ADMIN_PASS')

def test_login():
    if not ADMIN_PASS:
        print("ERR: KSC_ADMIN_PASS não configurada no .env")
        return False

    u64 = base64.b64encode(ADMIN_USER.encode()).decode()
    p64 = base64.b64encode(ADMIN_PASS.encode()).decode()

    # Cabeçalho exigido pelo KSC 16.x Linux
    auth_header = f'KSCBasic user="{u64}", pass="{p64}", internal="1"'
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(
        f"{SERVER}/api/v1.0/login",
        data=b"{}",
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            print(f"SUCCESS: Login bem-sucedido com usuário {ADMIN_USER}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"FAILED: HTTP {e.code} - {body}")
        return False
    except Exception as e:
        print(f"ERR: {e}")
        return False

if __name__ == "__main__":
    test_login()
