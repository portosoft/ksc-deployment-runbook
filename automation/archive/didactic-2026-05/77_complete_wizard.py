#!/usr/bin/env python3
import urllib.request
import urllib.error
import base64
import ssl
import json
import os
import sys
import re
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv


def build_validated_url(base_url: str, endpoint: str) -> str:
    try:
        # Minimal path validation
        if "/../" in base_url or re.search(r"/%2e%2e/", base_url, re.IGNORECASE):
            raise ValueError("Invalid path")

        parsed = urlparse(base_url)

        # Host check
        if not parsed.hostname:
            raise ValueError("Invalid host")
        allowed_domains = ["example.com"]  # add your allowed domains here
        if parsed.hostname.lower() not in allowed_domains:
            raise ValueError("Invalid host")

        # Validate path parameter
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", endpoint):
            raise ValueError("Invalid parameter")

        # Rebuild path from fixed literals + validated segments
        parsed = parsed._replace(path=f"/api/v1.0/{endpoint}")

        return urlunparse(parsed)
    except Exception:
        raise ValueError("Invalid URL")


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

    def call_api(endpoint, payload=b"{}"):
        url = build_validated_url(SERVER, endpoint)
        req = urllib.request.Request(
            url,
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
