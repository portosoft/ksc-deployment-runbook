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

print("Checking if we can download klnagent and web-console RPMs directly...")
shell.send(
    "wget https://products.s.kaspersky-labs.com/administrationkit/ksc10/16.2.0.1023/portuguese-BR-29665499-pt-BR/d98c7361838b447c97ec6bd847b9103d/klnagent64-16.2.0-1023.x86_64.rpm -O /home/suporte/klnagent64-16.2.0-1023.x86_64.rpm\n"
)
time.sleep(5)
out = shell.recv(65536).decode("utf-8", errors="replace")
print("klnagent download:")
print(out)

shell.send(
    "wget https://products.s.kaspersky-labs.com/administrationkit/ksc10/16.2.0.1023/portuguese-BR-29665499-pt-BR/fec0022d4fdf4ee48d1a16616239103d/ksc-web-console-16.2.11309.x86_64.rpm -O /home/suporte/ksc-web-console-16.2.11309.x86_64.rpm\n"
)
time.sleep(5)
out = shell.recv(65536).decode("utf-8", errors="replace")
print("ksc-web-console download:")
print(out)

client.close()
