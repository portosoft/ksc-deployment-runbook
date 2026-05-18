import paramiko
import os
import time
from dotenv import load_dotenv

load_dotenv("configs/env/ksc_vars.env")
host = os.getenv("KSC_HOST")
user = os.getenv("KSC_USER")
password = os.getenv("KSC_PASS")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)


def run_sudo(cmd):
    print(f"Executando: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"OUT: {out}")
    if err:
        print(f"ERR: {err}")
    return out


print("=" * 60)
print("FINAL PARTE 5: ROLLBACK CONTROLADO (LOCALE FIX)")
print("=" * 60)

# 5.2 Parar serviços
run_sudo("sudo -S systemctl stop kliam_srv kladminserver_srv")

# 5.3 Recriar banco ksciam (LOCALE pt_BR)
print("\n[5.3] Recriando banco ksciam...")
run_sudo(
    "sudo -S -u postgres psql -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ksciam' AND pid <> pg_backend_pid();\""
)
run_sudo('sudo -S -u postgres psql -c "DROP DATABASE IF EXISTS ksciam;"')
run_sudo(
    "sudo -S -u postgres psql -c \"CREATE DATABASE ksciam OWNER kluser ENCODING 'UTF8' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8';\""
)

# 5.4 Iniciar Administration Server
print("\n[5.4] Iniciando Administration Server...")
run_sudo("sudo -S systemctl start kladminserver_srv")

client.close()
print("\nBanco recriado. Aguardando 90 segundos...")
