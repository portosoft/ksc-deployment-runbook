import paramiko
import sys

hostname = "kscserver.tail8b9ae.ts.net"
username = "suporte"
password = "[REDACTED_SSH_PASS]"

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.RejectPolicy())

print(f"Connecting to {hostname}...")
client.connect(hostname, username=username, password=password)

stdin, stdout, stderr = client.exec_command(
    "systemctl list-units 'kl*' 'ksc*' --all --no-pager"
)
print(stdout.read().decode("utf-8", errors="replace"))

client.close()
