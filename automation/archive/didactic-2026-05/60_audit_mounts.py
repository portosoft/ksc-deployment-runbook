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
print("AUDITORIA DE MONTAGEM E SISTEMA DE ARQUIVOS")
print("=" * 60)

# 1. Verificar montagens
print("\n[1] Pontos de montagem (mount):")
stdin, stdout, stderr = client.exec_command("mount | grep -E '/var/opt|/var/log'")
print(stdout.read().decode().strip())

# 2. Verificar espaço em disco
print("\n[2] Espaço em disco (df -h):")
stdin, stdout, stderr = client.exec_command("df -h /var/opt/kaspersky/")
print(stdout.read().decode().strip())

# 3. Listar diretório pai em detalhes
print("\n[3] Listagem de klnagent_srv:")
stdin, stdout, stderr = client.exec_command(
    "sudo -S ls -la /var/opt/kaspersky/klnagent_srv/"
)
stdin.write(password + "\n")
stdin.flush()
print(stdout.read().decode().strip())

client.close()
