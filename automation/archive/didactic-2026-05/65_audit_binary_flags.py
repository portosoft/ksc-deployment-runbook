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
print("AUDITORIA DE BINÁRIO: KLSRVCONFIG")
print("=" * 60)

cmd = "strings /opt/kaspersky/ksc64/sbin/klsrvconfig | grep -iE 'dbname|dbpass|ias|iam' | head -n 30"
stdin, stdout, stderr = client.exec_command(cmd)

print(stdout.read().decode())
client.close()
