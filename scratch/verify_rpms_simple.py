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
            # Check for any line ending with # or $ followed by space, or just a shell prompt structure
            if re.search(r'(#|\$)\s*$', output):
                time.sleep(0.2)
                if shell.recv_ready():
                    output += shell.recv(4096).decode('utf-8', errors='replace')
                return output
        time.sleep(0.1)
    return output

print("Waiting for initial prompt...")
out = wait_for_prompt()
print("Initial:", repr(out))

print("Sending 'sudo su -'...")
shell.send("sudo su -\n")
time.sleep(1)
out = ""
if shell.recv_ready():
    out = shell.recv(4096).decode('utf-8', errors='replace')
print("Sudo output:", repr(out))
if "senha" in out.lower() or "password" in out.lower():
    shell.send(password + "\n")
    time.sleep(1)
    out = shell.recv(4096).decode('utf-8', errors='replace')
    print("Sudo post-password output:", repr(out))

# Check who we are
shell.send("whoami\n")
time.sleep(1)
out = shell.recv(4096).decode('utf-8', errors='replace')
print("whoami output:", repr(out))

print("Verifying RPMs...")
shell.send("ls -lh /home/suporte/*.rpm\n")
time.sleep(1)
out = shell.recv(4096).decode('utf-8', errors='replace')
print("ls output:", repr(out))

client.close()
