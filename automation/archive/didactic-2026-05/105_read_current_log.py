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
print("ANALISANDO: postgresql-Sat.log (HOJE)")
print("=" * 60)

cmd = "sudo -S tail -n 100 /var/lib/pgsql/data/log/postgresql-Sat.log"
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

logs = stdout.read().decode()
for line in logs.split("\n"):
    if any(
        term in line.lower() for term in ["kluser", "ksciam", "error", "fatal", "fail"]
    ):
        print(line)

client.close()
