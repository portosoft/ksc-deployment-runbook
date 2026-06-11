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
print("DIAGNÓSTICO DE INICIALIZAÇÃO: KLIAM")
print("=" * 60)

# Tenta rodar o comando manualmente para ver o erro direto no terminal
cmd = "sudo -S /opt/kaspersky/ksc64/sbin/kliam --config /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

print("--- STDOUT ---")
print(stdout.read().decode())
print("--- STDERR ---")
print(stderr.read().decode())

client.close()
