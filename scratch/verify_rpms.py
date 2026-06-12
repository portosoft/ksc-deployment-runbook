import os
import paramiko
import time
import sys
import re

hostname = os.getenv('KSC_HOST')
username = os.getenv('KSC_USER')
password = os.getenv('KSC_PASS')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

print(f"Connecting to {hostname}...")
client.connect(hostname, username=username, password=password)

shell = client.invoke_shell()

def wait_for_prompt(timeout=30):
    end_time = time.time() + timeout
    output = ""
    while time.time() < end_time:
        if shell.recv_ready():
            chunk = shell.recv(4096).decode('utf-8', errors='replace')
            output += chunk
            if re.search(r'(#|\$)\s*$', output):
                time.sleep(0.5)
                if shell.recv_ready():
                    output += shell.recv(4096).decode('utf-8', errors='replace')
                return output
        time.sleep(0.1)
    return output

print("Waiting for initial prompt...")
out = wait_for_prompt()

print("Sending 'sudo su -'...")
shell.send("sudo su -\n")
out = wait_for_prompt()
if "senha" in out.lower() or "password" in out.lower():
    shell.send(password + "\n")
    out = wait_for_prompt()

print("Verifying RPMs...")
shell.send("ls -lh /home/suporte/*.rpm\n")
out = wait_for_prompt()
print(out)

client.close()
