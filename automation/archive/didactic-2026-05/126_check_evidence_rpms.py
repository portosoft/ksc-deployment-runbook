import paramiko
import time
import sys
import re

hostname = "kscserver.tail8b9ae.ts.net"
username = "suporte"
password = "[REDACTED_SSH_PASS]"

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.RejectPolicy())

print(f"Connecting to {hostname}...")
client.connect(hostname, username=username, password=password)

shell = client.invoke_shell()


def wait_for_prompt(timeout=30):
    end_time = time.time() + timeout
    output = ""
    while time.time() < end_time:
        if shell.recv_ready():
            chunk = shell.recv(4096).decode("utf-8", errors="replace")
            output += chunk
            if re.search(r"(#|\$)\s*$", output):
                time.sleep(0.2)
                if shell.recv_ready():
                    output += shell.recv(4096).decode("utf-8", errors="replace")
                return output
        time.sleep(0.1)
    return output


print("Waiting for initial prompt...")
wait_for_prompt()

print("Sending 'sudo su -'...")
shell.send("sudo su -\n")
time.sleep(1)
out = shell.recv(4096).decode("utf-8", errors="replace")
if "senha" in out.lower() or "password" in out.lower():
    shell.send(password + "\n")
    time.sleep(1)
    shell.recv(4096)

print("Checking evidence directory contents...")
shell.send(
    "find /root/ksc_evidence_final/ /root/ksc_recovery_evidence/ -name '*.rpm' -o -name '*web-console*' -o -name '*klnagent*'\n"
)
time.sleep(3)
out = shell.recv(65536).decode("utf-8", errors="replace")
print("Evidence folders search:")
print(out)

client.close()
