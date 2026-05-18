#!/usr/bin/env python3
import urllib.request, base64, ssl, json, os, sys
from dotenv import load_dotenv

def force_plugin_init():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv('KSC_HOST')
    user = os.getenv('KSC_ADMIN_USER', 'KLAdmins')
    password = os.getenv('KSC_ADMIN_PASS')
    
    ctx = ssl._create_unverified_context()
    # Usando localhost pois vamos rodar via SSH
    SERVER = "https://127.0.0.1:13299"
    u64 = base64.b64encode(user.encode()).decode()
    p64 = base64.b64encode(password.encode()).decode()
    headers = {
        'Authorization': f'KSCBasic user="{u64}", pass="{p64}", internal="1"',
        'Content-Type': 'application/json'
    }

    def api(endpoint):
        req = urllib.request.Request(f"{SERVER}/api/v1.0/{endpoint}", data=b"{}", headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
                return True, r.read().decode()
        except Exception as e:
            return False, str(e)

    print("--- Forçando Inicialização de Plugins ---")
    # Disparar a verificação de plugins para forçar o carregamento da sidebar
    ok, resp = api("WstrPluginManagementService.CheckForUpdates")
    print(f"CheckUpdates: {'SUCCESS' if ok else 'FAIL (' + resp + ')'}")
    
    ok, resp = api("WstrPluginManagementService.GetPluginInfoList")
    print(f"GetPlugins: {'SUCCESS' if ok else 'FAIL (' + resp + ')'}")

if __name__ == "__main__":
    force_plugin_init()
