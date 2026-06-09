#!/bin/bash

echo "=== PARTE 5: ROLLBACK ==="
# 5.1 Backup obrigatorio do banco ksc
sudo -u postgres pg_dump ksc | sudo tee /tmp/ksc_backup_"$(date +%Y%m%d_%H%M)".sql > /dev/null
ls -lh /tmp/ksc_backup_*.sql || true

# 5.2 Parar todos os servicos KSC
sudo systemctl stop KSCWebConsole KSCSvcWebConsole kliam_srv kladminserver_srv || true

# 5.3 Recriar apenas o banco ksciam
sudo -u postgres psql << 'SQL'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE datname = 'ksciam' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ksciam;
CREATE DATABASE ksciam OWNER kluser
  ENCODING 'UTF8'
  LC_COLLATE 'en_US.UTF-8'
  LC_CTYPE 'en_US.UTF-8';
SQL

# 5.4 Iniciar apenas o kladminserver e aguardar recriar schema
sudo systemctl start kladminserver_srv
echo "Aguardando 90s para o kladminserver recriar o schema IAM..."
sleep 90

# 5.5 Verificar se schema IAM foi recriado
sudo -u postgres psql -d ksciam << 'SQL'
SELECT table_schema, COUNT(*) AS total
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
GROUP BY table_schema
ORDER BY table_schema;
SQL

# 5.6 Iniciar servicos restantes
sudo systemctl start kliam_srv || true
sleep 20
sudo systemctl start KSCSvcWebConsole || true
sleep 5
sudo systemctl start KSCWebConsole || true
sleep 20

echo "=== PARTE 2: FIX 2FA SCRIPT CREATION ==="
cat > /tmp/fix_2fa_flow.py << 'PYEOF'
#!/usr/bin/env python3
import urllib.request
import urllib.error
import base64
import ssl
import json
import os
import sys

ctx = ssl._create_unverified_context()
SRV  = "https://127.0.0.1:13299"
USER = os.getenv("KSC_ADMIN_USER", "KLAdmins")
PASS = os.getenv("KSC_ADMIN_PASS", "")

if not PASS:
    print("ERRO: KSC_ADMIN_PASS nao definida.")
    sys.exit(1)

u64 = base64.b64encode(USER.encode()).decode()
p64 = base64.b64encode(PASS.encode()).decode()

def api_post(endpoint, payload=b"{}", extra_headers=None):
    headers = {
        "Authorization": f'KSCBasic user="{u64}", pass="{p64}", internal="1"',
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(
        f"{SRV}/api/v1.0/{endpoint}",
        data=payload,
        headers=headers,
        method="POST"
    )
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=15)
        return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()

print("=" * 60)
print(f"PASSO 1: Login como '{USER}' — capturando desafio 2FA")
print("=" * 60)

status, headers, body = api_post("login")
print(f"HTTP: {status}")
www_auth = headers.get("Www-Authenticate", headers.get("WWW-Authenticate", ""))
session  = headers.get("X-Ksc-Session",   headers.get("x-ksc-session", ""))
print(f"WWW-Authenticate: {www_auth}")
print(f"X-KSC-Session:    {session}")
print(f"Body:             {body[:200]}")

if status == 200:
    print("\n[OK] LOGIN BEM-SUCEDIDO — 2FA nao esta bloqueando!")
    sys.exit(0)

if "totpreg" in www_auth:
    print("\nCENARIO A: Primeiro registro de TOTP necessario")
    s2, h2, b2 = api_post(
        "TotpRegistration.GenerateSecret",
        extra_headers={"X-KSC-Session": session}
    )
    print(f"GenerateSecret HTTP: {s2}")

    try:
        data = json.loads(b2)
        secret_key = data.get("pSecret", {}).get("KLTOTP_SECRET_KEY", "")
        secret_id = data.get("pSecret", {}).get("KLTOTP_SECRET_ID", "")
        print(f"SECRET KEY: {secret_key}")
        print(f"SECRET ID: {secret_id}")
        print(f"SESSION: {session}")
        print("MFA_PENDING_REGISTRATION")
    except Exception as e:
        print(f"Failed to parse: {e}")

elif "totp" in www_auth and "totpreg" not in www_auth:
    print("\nCENARIO B: TOTP ja configurado")
    print(f"SESSION: {session}")
    print("MFA_PENDING_CODE")

PYEOF

echo "=== PARTE 2: EXECUCAO ==="
sudo KSC_ADMIN_USER="${KSC_ADMIN_USER:-KLAdmins}" KSC_ADMIN_PASS="${KSC_ADMIN_PASS}" python3 /tmp/fix_2fa_flow.py
