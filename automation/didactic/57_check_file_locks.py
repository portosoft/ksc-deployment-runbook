import paramiko
import os
from dotenv import load_dotenv

load_dotenv("configs/env/ksc_vars.env")
host = os.getenv("KSC_HOST")
user = os.getenv("KSC_USER")
password = os.getenv("KSC_PASS")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

print("=" * 60)
print("AUDITORIA DE BLOQUEIO: iam_config.yaml")
print("=" * 60)

target = "/var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"

# 1. Verificar atributos (lsattr)
print("\n[1] Atributos (lsattr):")
stdin, stdout, stderr = client.exec_command(f"lsattr {target}")
print(stdout.read().decode().strip())

# 2. Verificar quem está usando o arquivo (lsof)
print("\n[2] Processos usando o arquivo (lsof):")
stdin, stdout, stderr = client.exec_command(f"sudo -S lsof {target}")
stdin.write(password + "\n")
stdin.flush()
print(stdout.read().decode().strip())

# 3. Tentar remover o arquivo antes de mover o novo
print("\n[3] Tentando remoção forçada (rm -f):")
stdin, stdout, stderr = client.exec_command(f"sudo -S rm -f {target}")
stdin.write(password + "\n")
stdin.flush()
print(stdout.read().decode().strip())
print(stderr.read().decode().strip())

client.close()
