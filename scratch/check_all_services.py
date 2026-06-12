import os
import paramiko
import sys

hostname = os.getenv('KSC_HOST')
username = os.getenv('KSC_USER')
password = os.getenv('KSC_PASS')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

print(f"Connecting to {hostname}...")
client.connect(hostname, username=username, password=password)

stdin, stdout, stderr = client.exec_command("systemctl list-units 'kl*' 'ksc*' --all --no-pager")
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
