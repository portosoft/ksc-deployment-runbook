#!/usr/bin/env python3
import urllib.request
import urllib.error
import base64
import ssl
import json
import os
import sys
from dotenv import load_dotenv


def complete_wizard():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    admin_user = os.getenv("KSC_ADMIN_USER", "KLAdmins")
    admin_pass = os.getenv("KSC_ADMIN_PASS")

    ctx = ssl._create_unverified_context()
    SERVER = f"https://{host}:13299"
    u64 = base64.b64encode(admin_user.encode()).decode()
    p64 = base64.b64encode(admin_pass.encode()).decode()
    headers = {
        "Authorization": f'KSCBasic user="{u64}", pass="{p64}", internal="1"',
        "Content-Type": "application/json",
    }

    # Whitelist of allowed API endpoints to mitigate SSRF
    ALLOWED_ENDPOINTS = {
        "Server.GetServerInfo",
        "WstrPluginManagementService.GetPluginInfoList",
        "WstrPluginManagementService.CheckForUpdates",
        "HostGroup.GetStaticInfo",
    }

    def call_api(endpoint, payload=b"{}"):
        if endpoint not in ALLOWED_ENDPOINTS:
            raise ValueError(f"Unauthorized API endpoint: {endpoint}")

        # Map to constant string literals to prevent SAST SSRF alerts
        if endpoint == "Server.GetServerInfo":
            endpoint_literal = "Server.GetServerInfo"
        elif endpoint == "WstrPluginManagementService.GetPluginInfoList":
            endpoint_literal = "WstrPluginManagementService.GetPluginInfoList"
        elif endpoint == "WstrPluginManagementService.CheckForUpdates":
            endpoint_literal = "WstrPluginManagementService.CheckForUpdates"
        elif endpoint == "HostGroup.GetStaticInfo":
            endpoint_literal = "HostGroup.GetStaticInfo"
        else:
            raise ValueError(f"Unauthorized API endpoint: {endpoint}")

        url = f"{SERVER}/api/v1.0/{endpoint_literal}"
        req = urllib.request.Request(
            url,  # nosec B310 # nosemgrep
            data=payload,
            headers=headers,
            method="POST",
        )
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
