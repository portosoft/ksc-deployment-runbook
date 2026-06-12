import paramiko
import os
from dotenv import load_dotenv

load_dotenv("configs/env/ksc_vars.env")
host = os.getenv("KSC_HOST")
user = os.getenv("KSC_USER")
password = os.getenv("KSC_PASS")

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.RejectPolicy())
client.connect(host, username=user, password=password)

print("=" * 60)
print("FORÇANDO CRIAÇÃO DO DIRETÓRIO IAM")
print("=" * 60)

# Comando encadeado para garantir que a validação ocorra imediatamente após a criação
cmd = "sudo -S bash -c 'mkdir -v -p /var/opt/kaspersky/klnagent_srv/iam/ && touch /var/opt/kaspersky/klnagent_srv/iam/test.txt && ls -ld /var/opt/kaspersky/klnagent_srv/iam/'"

stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

print("--- STDOUT ---")
print(stdout.read().decode().strip())
print("--- STDERR ---")
print(stderr.read().decode().strip())

client.close()
