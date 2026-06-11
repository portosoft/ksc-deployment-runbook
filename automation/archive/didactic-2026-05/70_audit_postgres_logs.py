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
print("AUDITORIA DE LOGS: POSTGRESQL")
print("=" * 60)

# Busca os arquivos de log dinamicamente
cmd = "sudo -S find /var/lib/pgsql/data/log/ -name '*.log' -exec tail -n 50 {} +"
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

logs = stdout.read().decode()
# Filtrar por kluser ou ksciam
for line in logs.split("\n"):
    if any(term in line.lower() for term in ["kluser", "ksciam", "error", "fatal"]):
        print(line)

client.close()
