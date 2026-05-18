import paramiko
import os
import time
from dotenv import load_dotenv

load_dotenv("configs/env/ksc_vars.env")
host = os.getenv("KSC_HOST")
user = os.getenv("KSC_USER")
password = os.getenv("KSC_PASS")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

print("=" * 60)
print("REINICIANDO KLIAM_SRV E AUDITANDO BANCO")
print("=" * 60)

# Reiniciar serviço
print("[1] Reiniciando kliam_srv...")
stdin, stdout, stderr = client.exec_command("sudo -S systemctl restart kliam_srv")
stdin.write(password + "\n")
stdin.flush()
time.sleep(15) # Aguarda inicialização e migrações

# Verificar contagem de tabelas
print("\n[2] Verificando densidade de tabelas no ksciam...")
sql = "SELECT table_schema, COUNT(*) AS total FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog','information_schema') GROUP BY table_schema ORDER BY table_schema;"
stdin, stdout, stderr = client.exec_command(f"sudo -S -u postgres psql -d ksciam -c \"{sql}\"")
stdin.write(password + "\n")
stdin.flush()

print(stdout.read().decode())
client.close()
