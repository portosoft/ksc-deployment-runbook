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
print("AUDITORIA: iam_config.yaml")
print("=" * 60)

cmd = "sudo -S cat /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

content = stdout.read().decode()
# Filtrar para não exibir a senha no log (Segurança)
for line in content.split("\n"):
    if "dbms_" in line or "database" in line:
        if "password" in line.lower():
            print(f"{line.split(':')[0]}: [HIDDEN]")
        else:
            print(line)

client.close()
