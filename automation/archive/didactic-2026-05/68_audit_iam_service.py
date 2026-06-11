import paramiko
import os
from dotenv import load_dotenv

load_dotenv("configs/env/ksc_vars.env")
host = os.getenv("KSC_HOST")
user = os.getenv("KSC_USER")
password = os.getenv("KSC_PASS")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
client.connect(host, username=user, password=password)

print("=" * 60)
print("AUDITORIA DE SERVIÇO: KLIAM_SRV")
print("=" * 60)

# 1. Verificar processo
print("\n[1] Processo em execução:")
stdin, stdout, stderr = client.exec_command("ps -ef | grep kliam | grep -v grep")
print(stdout.read().decode().strip())

# 2. Verificar definição da unidade systemd
print("\n[2] Definição da unidade (systemctl cat):")
stdin, stdout, stderr = client.exec_command("systemctl cat kliam_srv")
print(stdout.read().decode().strip())

client.close()
