import paramiko
import time
import sys
import re

hostname = "kscserver.tail8b9ae.ts.net"
username = "suporte"
password = "[REDACTED_SSH_PASS]"

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

commands = """
echo "=== 2.2 ==="
cat > /etc/ksc-web-console-setup.json << 'JSON'
{
  "address": "kscserver.tail8b9ae.ts.net",
  "port": 8080,
  "trusted_cert": "",
  "trusted_cert_key": "",
  "defaultLanguageId": "pt-BR",
  "openAPIServers": [
    {
      "address": "kscserver.tail8b9ae.ts.net",
      "port": 13000,
      "openApiPort": 13299
    }
  ]
}
JSON
cat /etc/ksc-web-console-setup.json

echo "=== 2.3 ==="
rpm -ivh /home/suporte/ksc64-16.2.0-1023.x86_64.rpm
rpm -qi ksc64 | head -5

echo "=== 2.4 ==="
id ksc 2>/dev/null || useradd -r -s /sbin/nologin ksc
getent group kladmins 2>/dev/null || groupadd kladmins
usermod -aG kladmins ksc
id ksc

echo "=== DONE_PART_2_PRE ==="
"""

print("Executing pre-postinstall setup...")
shell.send("cat << 'EOF_SCRIPT' > /tmp/part2_pre.sh\n" + commands + "\nEOF_SCRIPT\n")
wait_for_prompt()

shell.send("bash /tmp/part2_pre.sh\n")

final_out = ""
end_time = time.time() + 180
while time.time() < end_time:
    if shell.recv_ready():
        chunk = shell.recv(4096).decode("utf-8", errors="replace")
        final_out += chunk
        if "=== DONE_PART_2_PRE ===" in final_out and re.search(
            r"(#|\$)\s*$", final_out
        ):
            break
    time.sleep(0.1)

print("--- OUTPUT ---")
print(final_out)
print("--------------")

client.close()
