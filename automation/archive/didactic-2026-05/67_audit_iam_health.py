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
print("AUDITORIA DE SAÚDE DO BANCO KSCIAM")
print("=" * 60)

sql = """
SELECT table_schema, COUNT(*) AS total
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog','information_schema')
GROUP BY table_schema
ORDER BY table_schema;
"""

cmd = f'sudo -S -u postgres psql -d ksciam -c "{sql}"'
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

print(stdout.read().decode())
print(stderr.read().decode())

client.close()
