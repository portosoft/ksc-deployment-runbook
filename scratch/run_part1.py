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
            # Check for root prompt (#) or user prompt ($) or password prompt
            if re.search(r'(#|\$)\s*$', output) or "senha" in output.lower() or "password" in output.lower():
                # Let's wait a tiny bit more just in case there's more data
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

print("Now as root.")

commands = """
echo "=== 1.1 ==="
mkdir -p /root/ksc_evidence_final/
rpm -qa | grep -iE 'kaspersky|ksc|kl' > /root/ksc_evidence_final/rpms_instalados.txt
sudo -u postgres psql -c "\\l+" > /root/ksc_evidence_final/databases.txt 2>&1
for svc in kladminserver_srv kliam_srv KSCWebConsole KSCSvcWebConsole klnagent_srv; do
  echo "$svc: $(systemctl is-active $svc 2>/dev/null)"
done > /root/ksc_evidence_final/services.txt
cat /root/ksc_evidence_final/services.txt

echo "=== 1.2 ==="
for svc in KSCWebConsole KSCSvcWebConsole kliam_srv kladminserver_srv klnagent_srv; do
  systemctl stop $svc 2>/dev/null || true
done
sleep 5
ps aux | grep -iE 'klserver|kliam|klweb|kscweb' | grep -v grep

echo "=== 1.3 ==="
rpm -qa | grep -iE 'kaspersky|^ksc|^kl' | xargs -r rpm -e --noscripts 2>&1 | head -30
rpm -qa | grep -iE 'kaspersky|^ksc|^kl'

echo "=== 1.4 ==="
DATE=$(date +%Y%m%d_%H%M)
mv /opt/kaspersky /root/ksc_evidence_final/opt_kaspersky_$DATE 2>/dev/null || true
mv /var/opt/kaspersky /root/ksc_evidence_final/varopt_kaspersky_$DATE 2>/dev/null || true
mv /etc/opt/kaspersky /root/ksc_evidence_final/etcopt_kaspersky_$DATE 2>/dev/null || true
echo "Diretórios movidos para evidência."

echo "=== 1.5 ==="
sudo -u postgres psql << 'SQL'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('ksc','ksciam') AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ksc;
DROP DATABASE IF EXISTS ksciam;
DROP ROLE IF EXISTS kluser;
SELECT datname FROM pg_database WHERE datname IN ('ksc','ksciam');
SQL

echo "=== 1.6 ==="
sudo -u postgres psql << 'SQL'
CREATE ROLE kluser WITH LOGIN PASSWORD 'Kl@2026Secure';
ALTER ROLE kluser CREATEDB;
CREATE DATABASE ksc OWNER kluser ENCODING 'UTF8' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8' TEMPLATE template0;
CREATE DATABASE ksciam OWNER kluser ENCODING 'UTF8' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8' TEMPLATE template0;
GRANT ALL PRIVILEGES ON DATABASE ksc TO kluser;
GRANT ALL PRIVILEGES ON DATABASE ksciam TO kluser;
SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database WHERE datname IN ('ksc','ksciam');
SQL

echo "=== 1.7 ==="
sudo -u postgres psql -t -c "SHOW standard_conforming_strings;"

echo "=== DONE_PART_1 ==="
"""

print("Executing commands...")
# We send the script as a block
shell.send("cat << 'EOF_SCRIPT' > /tmp/part1.sh\n" + commands + "\nEOF_SCRIPT\n")
wait_for_prompt()

shell.send("bash /tmp/part1.sh\n")

final_out = ""
end_time = time.time() + 120
while time.time() < end_time:
    if shell.recv_ready():
        chunk = shell.recv(4096).decode('utf-8', errors='replace')
        final_out += chunk
        if "=== DONE_PART_1 ===" in final_out and re.search(r'(#|\$)\s*$', final_out):
            break
    time.sleep(0.1)

print("--- OUTPUT ---")
print(final_out)
print("--------------")

client.close()
