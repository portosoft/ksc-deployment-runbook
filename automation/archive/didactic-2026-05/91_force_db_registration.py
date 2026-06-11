import paramiko
import os
from dotenv import load_dotenv

load_dotenv("configs/env/ksc_vars.env")
host = os.getenv("KSC_HOST")
user = os.getenv("KSC_USER")
password = os.getenv("KSC_PASS")
db_user = os.getenv("KSC_DB_USER")
db_pass = os.getenv("KSC_DB_PASS")
db_name = os.getenv("KSC_IAM_NAME")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
client.connect(host, username=user, password=password)

print("=" * 60)
print("FORÇANDO REGISTRO DO BANCO IAM NO SERVIDOR")
print("=" * 60)

# O klsrvconfig vincula o banco de dados ao servidor de administração
# Usamos os parâmetros de banco definidos no .env
cmd = f"sudo -S /opt/kaspersky/ksc64/sbin/klsrvconfig -dbname {db_name} -dbuser {db_user} -dbpass '{db_pass}'"
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

print("--- Saída do klsrvconfig ---")
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
