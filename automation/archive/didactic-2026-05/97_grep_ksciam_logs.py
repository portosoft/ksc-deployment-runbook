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
print("BUSCANDO 'KSCIAM' NO AK_SERVER.LOG")
print("=" * 60)

cmd = "sudo -S grep -i 'ksciam' /var/log/kaspersky/ak_server.log | tail -n 50"
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

print(stdout.read().decode())
client.close()
