import paramiko
import time

import os

host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())


def run_sudo(cmd):
    # Envolve em sudo garantindo a senha
    full_cmd = f"echo '{password}' | sudo -S sh -c '{cmd}'"
    print(f"Executando: {cmd[:100]}...")
    stdin, stdout, stderr = client.exec_command(full_cmd)
    out = stdout.read().decode("utf-8")
    err = stderr.read().decode("utf-8")
    return out, err


try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    print("=== INICIANDO PARTE 5: ROLLBACK ===")

    # 5.1 Backup obrigatorio
    out, err = run_sudo(
        "sudo -u postgres pg_dump ksc > /tmp/ksc_backup_$(date +%Y%m%d_%H%M).sql && ls -lh /tmp/ksc_backup_*.sql"
    )
    print("5.1 Backup:", out, err)

    # 5.2 Parar todos os servicos KSC
    out, err = run_sudo(
        "systemctl stop KSCWebConsole KSCSvcWebConsole kliam_srv kladminserver_srv"
    )
    print("5.2 Parar servicos:", out, err)

    # 5.3 Recriar apenas o banco ksciam
    sql_script = """
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ksciam' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ksciam;
CREATE DATABASE ksciam OWNER kluser ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';
"""
    out, err = run_sudo(f'sudo -u postgres psql -c "{sql_script}"')
    print("5.3 Recriar banco:", out, err)

    # 5.4 Iniciar kladminserver_srv
    out, err = run_sudo("systemctl start kladminserver_srv")
    print("5.4 Iniciar kladminserver_srv:", out, err)
    print("Aguardando 90s...")
    time.sleep(90)

    # 5.5 Verificar schema
    sql_check = "SELECT table_schema, COUNT(*) AS total FROM information_schema.tables WHERE table_type = 'BASE TABLE' GROUP BY table_schema ORDER BY table_schema;"
    out, err = run_sudo(f'sudo -u postgres psql -d ksciam -c "{sql_check}"')
    print("5.5 Schema:", out, err)

    # 5.6 Iniciar o restante
    print("5.6 Iniciando servicos...")
    run_sudo("systemctl start kliam_srv")
    time.sleep(20)
    run_sudo("systemctl start KSCSvcWebConsole")
    time.sleep(5)
    run_sudo("systemctl start KSCWebConsole")
    time.sleep(20)

    print("=== INICIANDO PARTE 2: FIX 2FA FLOW ===")

    p2_script = """cat > /tmp/fix_2fa_flow.py << 'PYEOF'
#!/usr/bin/env python3
import urllib.request, urllib.error, base64, ssl, json, os, sys
ctx = ssl._create_unverified_context()
SRV = "https://127.0.0.1:13299"
USER = os.getenv("KSC_ADMIN_USER", "KLAdmins")
PASS = os.getenv("KSC_ADMIN_PASS", "")
if not PASS: sys.exit(1)
u64 = base64.b64encode(USER.encode()).decode()
p64 = base64.b64encode(PASS.encode()).decode()

def api_post(endpoint, payload=b"{}", extra_headers=None):
    headers = {"Authorization": f'KSCBasic user="{u64}", pass="{p64}", internal="1"', "Content-Type": "application/json"}
    if extra_headers: headers.update(extra_headers)
    req = urllib.request.Request(f"{SRV}/api/v1.0/{endpoint}", data=payload, headers=headers, method="POST")
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=15)
        return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()

status, headers, body = api_post("login")
www_auth = headers.get("Www-Authenticate", headers.get("WWW-Authenticate", ""))
session  = headers.get("X-Ksc-Session",   headers.get("x-ksc-session", ""))

if status == 200:
    print("LOGIN BEM-SUCEDIDO")
    sys.exit(0)

if "totpreg" in www_auth:
    print("REGISTRO_TOTP_NECESSARIO")
    # Tenta excluir mesmo que o login nao tenha completado, se nao for possivel
elif "totp" in www_auth:
    print("CODIGO_TOTP_NECESSARIO")
else:
    print(f"HTTP {status} {www_auth}")
PYEOF
"""
    out, err = run_sudo(p2_script)
    out, err = run_sudo(
        "KSC_ADMIN_USER=KLAdmins KSC_ADMIN_PASS='Ksc@2026' python3 /tmp/fix_2fa_flow.py"
    )
    print("P2 OUTPUT:", out, err)

except Exception as e:
    print(e)
finally:
    client.close()
