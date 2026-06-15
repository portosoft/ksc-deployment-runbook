import os
import paramiko
import time
import sys
import re

hostname = os.getenv('KSC_HOST')
username = os.getenv('KSC_USER')
password = os.getenv('KSC_PASS')
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.RejectPolicy())

print(f"Connecting to {hostname}...")
client.connect(hostname, username=username, password=password)

shell = client.invoke_shell()

def send_and_wait(cmd, timeout=5):
    shell.send(cmd + "\n")
    time.sleep(1)
    output = ""
    start = time.time()
    while time.time() - start < timeout:
        if shell.recv_ready():
            output += shell.recv(4096).decode('utf-8', errors='replace')
        time.sleep(0.1)
    return output

# sudo su -
shell.send("sudo su -\n")
time.sleep(1)
if shell.recv_ready():
    out = shell.recv(4096).decode('utf-8', errors='replace')
    if "senha" in out.lower() or "password" in out.lower():
        shell.send(password + "\n")
        time.sleep(1)
        shell.recv(4096)

print("Checking KSC and KLIAM service statuses (with _srv suffix):")
services_status = send_and_wait("systemctl status kladminserver_srv klwebsrv_srv kliam_srv klnagent_srv --no-pager")

# Print safely in Windows CLI
try:
    sys.stdout.write(services_status.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
except Exception:
    print(services_status.encode('ascii', errors='replace').decode('ascii'))

client.close()
