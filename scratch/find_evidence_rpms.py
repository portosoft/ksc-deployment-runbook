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
                time.sleep(0.2)
                if shell.recv_ready():
                    output += shell.recv(4096).decode('utf-8', errors='replace')
                return output
        time.sleep(0.1)
    return output

print("Waiting for initial prompt...")
wait_for_prompt()

print("Sending 'sudo su -'...")
shell.send("sudo su -\n")
time.sleep(1)
out = shell.recv(4096).decode('utf-8', errors='replace')
if "senha" in out.lower() or "password" in out.lower():
    shell.send(password + "\n")
    time.sleep(1)
    shell.recv(4096)

print("Checking old klnagent_srv/1093 backup folders for rpms...")
shell.send("find /root/ksc_evidence_final/ /root/ksc_recovery_evidence/ -name '*.rpm'\n")
time.sleep(2)
out = shell.recv(65536).decode('utf-8', errors='replace')
print("Find RPMs in evidence/recovery folders:")
print(out)

client.close()
