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
print("AUDITORIA DE DIRETÓRIO: IAM CONFIG")
print("=" * 60)

# 1. Verificar diretório pai
print("\n[1] Permissões do diretório:")
stdin, stdout, stderr = client.exec_command(
    "ls -ld /var/opt/kaspersky/klnagent_srv/iam/"
)
print(stdout.read().decode().strip())

# 2. Listar conteúdo
print("\n[2] Conteúdo do diretório:")
stdin, stdout, stderr = client.exec_command(
    "ls -la /var/opt/kaspersky/klnagent_srv/iam/"
)
print(stdout.read().decode().strip())

client.close()
