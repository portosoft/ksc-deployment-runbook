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
print("VERIFICANDO CONEXÕES ATIVAS: KSCIAM")
print("=" * 60)

sql = "SELECT datname, usename, application_name, state FROM pg_stat_activity WHERE datname = 'ksciam';"

cmd = f'sudo -S -u postgres psql -c "{sql}"'
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

print(stdout.read().decode())
client.close()
