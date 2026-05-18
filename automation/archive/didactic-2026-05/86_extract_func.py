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

# Busca o número da linha de forma isolada
stdin, stdout, stderr = client.exec_command("grep -n 'sub klserver_register' /opt/kaspersky/ksc64/lib/bin/setup/appdata.pm")
line_info = stdout.read().decode().strip()

if line_info:
    line_num = int(line_info.split(":")[0])
    print(f"DEBUG: Function found at line {line_num}")
    # Lê as próximas 200 linhas para garantir que pegamos o corpo todo
    cmd_read = f"sed -n '{line_num},+200p' /opt/kaspersky/ksc64/lib/bin/setup/appdata.pm"
    stdin_r, stdout_r, stderr_r = client.exec_command(cmd_read)
    print("--- FUNCTION CODE ---")
    print(stdout_r.read().decode())
else:
    print("ERROR: klserver_register not found")

client.close()
