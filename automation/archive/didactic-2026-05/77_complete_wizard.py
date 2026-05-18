#!/usr/bin/env python3
import urllib.request, urllib.error, base64, ssl, json, os, sys
from dotenv import load_dotenv

def complete_wizard():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv('KSC_HOST')
    admin_user = os.getenv('KSC_ADMIN_USER', 'KLAdmins')
    admin_pass = os.getenv('KSC_ADMIN_PASS')
    
    ctx = ssl._create_unverified_context()
    SERVER = f"https://{host}:13299"
    u64 = base64.b64encode(admin_user.encode()).decode()
    p64 = base64.b64encode(admin_pass.encode()).decode()
    headers = {
        'Authorization': f'KSCBasic user="{u64}", pass="{p64}", internal="1"',
        'Content-Type': 'application/json'
    }

    def call_api(endpoint, payload=b"{}"):
        req = urllib.request.Request(f"{SERVER}/api/v1.0/{endpoint}", data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
                return True, r.read().decode()
        except Exception as e:
            return False, str(e)

    print("--- Destravando KSC via API ---")
    
    # 1. Obter informações do servidor
    ok, info = call_api("Server.GetServerInfo")
    print(f"Server Info: {'OK' if ok else 'FAIL'}")

    # 2. Verificar Plugins
    ok, plugins = call_api("WstrPluginManagementService.GetPluginInfoList")
    print(f"Plugins List: {'OK' if ok else 'FAIL'}")
    
    # 3. Forçar o 'CheckForUpdates' para os plugins (isso ajuda a popular a sidebar)
    ok, update = call_api("WstrPluginManagementService.CheckForUpdates")
    print(f"Check Updates: {'OK' if ok else 'FAIL'}")

    # 4. Tentar listar grupos (se falhar com 403, o wizard é obrigatório)
    ok, groups = call_api("HostGroup.GetStaticInfo")
    print(f"Access Test (Groups): {'OK' if ok else 'FAIL'}")

if __name__ == "__main__":
    complete_wizard()
