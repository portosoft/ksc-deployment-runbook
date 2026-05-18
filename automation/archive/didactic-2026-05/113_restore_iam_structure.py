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
print("RESTAURANDO ESTRUTURA DE DIRETÓRIOS IAM")
print("=" * 60)

def run_sudo(cmd):
    print(f"Executando: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode().strip())
    print(stderr.read().decode().strip())

# 1. Criar diretório
run_sudo("sudo -S mkdir -p /var/opt/kaspersky/klnagent_srv/iam/")

# 2. Definir permissões e dono (Baseado na unidade systemd que usa User=ksc)
run_sudo("sudo -S chown ksc:kladmins /var/opt/kaspersky/klnagent_srv/iam/")
run_sudo("sudo -S chmod 750 /var/opt/kaspersky/klnagent_srv/iam/")

# 3. Validar criação
print("\nValidando estrutura:")
stdin, stdout, stderr = client.exec_command("ls -ld /var/opt/kaspersky/klnagent_srv/iam/")
print(stdout.read().decode().strip())

client.close()
