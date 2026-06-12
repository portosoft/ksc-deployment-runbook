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
print("AUDITORIA DE LOGS: KLADMINSERVER_SRV")
print("=" * 60)

cmd = "sudo -S journalctl -u kladminserver_srv --no-pager -n 100"
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

logs = stdout.read().decode()
# Filtragem manual no Python para evitar erros de shell
for line in logs.split("\n"):
    if any(
        term in line.lower()
        for term in ["iam", "ksciam", "identity", "migration", "schema", "error"]
    ):
        print(line)

client.close()
