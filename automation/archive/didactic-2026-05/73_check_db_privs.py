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
print("AUDITORIA DE PRIVILÉGIOS: KLUSER EM KSCIAM")
print("=" * 60)

# Verifica privilégios de criação e listagem de esquemas
sql = """
SELECT 
    has_database_privilege('kluser', 'ksciam', 'CREATE') as can_create,
    has_database_privilege('kluser', 'ksciam', 'CONNECT') as can_connect;
SELECT schema_name FROM information_schema.schemata;
"""

cmd = f"sudo -S -u postgres psql -d ksciam -c \"{sql}\""
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

print(stdout.read().decode())
client.close()
