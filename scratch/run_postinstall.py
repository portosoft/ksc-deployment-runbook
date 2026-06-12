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

print("Starting postinstall.pl wizard...")
shell.send("LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl\n")

log = ""

# Let's guide the wizard!
# We will read chunks and inspect what it asks.
for i in range(250):
    time.sleep(0.2)
    if shell.recv_ready():
        chunk = shell.recv(4096).decode('utf-8', errors='replace')
        log += chunk
        try:
            sys.stdout.write(chunk.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
            sys.stdout.flush()
        except Exception:
            pass

    lower_log = log.lower()

    # If the pager is active ("--Mais--" or "--More--"), we send space bar to page down
    if re.search(r'--mais--\(\d+%\)|--more--\(\d+%\)', lower_log):
        shell.send(" ")
        # Remove pager prompt from log to avoid matches in next loop
        log = re.sub(r'--mais--\(\d+%\)|--more--\(\d+%\)', '', log, flags=re.IGNORECASE)
        time.sleep(0.1)
        continue

    # EULA Accept prompt
    if "enter 'y' to confirm that you understand and accept the terms of the end" in lower_log and re.search(r'\[[nr]\]:\s*$', log):
        shell.send("Y\n")
        log = ""
        print("\n[AUTO-SENT: Y (EULA)]")
        time.sleep(1)
        continue

    # KSN Agreement Accept prompt
    if "kaspersky security network" in lower_log and "ksn" in lower_log and re.search(r'\[[nr]\]:\s*$', log):
        shell.send("Y\n")
        log = ""
        print("\n[AUTO-SENT: Y (KSN)]")
        time.sleep(1)
        continue

    # DBMS Selection prompt
    if "choose dbms type" in lower_log and re.search(r'\]:\s*$', log):
        match = re.search(r'(\d+)\.\s+postgresql', lower_log)
        if match:
            db_num = match.group(1)
            shell.send(f"{db_num}\n")
            print(f"\n[AUTO-SENT DBMS: {db_num}]")
        else:
            shell.send("1\n")
            print("\n[AUTO-SENT DBMS: 1 (Fallback)]")
        log = ""
        time.sleep(1)
        continue

    # Database server hostname
    if "database server hostname" in lower_log and re.search(r'\]:\s*$', log):
        shell.send("127.0.0.1\n")
        log = ""
        print("\n[AUTO-SENT HOSTNAME: 127.0.0.1]")
        time.sleep(1)
        continue

    # Database server port
    if "database server port" in lower_log and re.search(r'\]:\s*$', log):
        shell.send("5432\n")
        log = ""
        print("\n[AUTO-SENT PORT: 5432]")
        time.sleep(1)
        continue

    # Database name
    if "database name [ksc]" in lower_log and re.search(r'\]:\s*$', log):
        shell.send("ksc\n")
        log = ""
        print("\n[AUTO-SENT DB NAME: ksc]")
        time.sleep(1)
        continue

    # Database name for IAM
    if "identity and access management" in lower_log and re.search(r'\]:\s*$', log):
        shell.send("ksciam\n")
        log = ""
        print("\n[AUTO-SENT IAM DB: ksciam]")
        time.sleep(1)
        continue

    # Database user name
    if "dbms user name" in lower_log and re.search(r'\]:\s*$', log):
        shell.send("kluser\n")
        log = ""
        print("\n[AUTO-SENT DB USER: kluser]")
        time.sleep(1)
        continue

    # Database user password
    if "dbms password:" in lower_log and log.endswith(": "):
        shell.send("Kl@2026Secure\n")
        log = ""
        print("\n[AUTO-SENT DB PASS: ******]")
        time.sleep(1.5)
        continue

    # Administration Server FQDN
    if "administration server ip address or fqdn" in lower_log and re.search(r'\]:\s*$', log):
        shell.send("kscserver.tail8b9ae.ts.net\n")
        log = ""
        print("\n[AUTO-SENT FQDN: kscserver.tail8b9ae.ts.net]")
        time.sleep(1)
        continue

    # Account name under which the service will run
    if "service will run" in lower_log and re.search(r'\]:\s*$', log):
        shell.send("ksc\n")
        log = ""
        print("\n[AUTO-SENT RUN AS: ksc]")
        time.sleep(1)
        continue

    # Security group name for KSC administrators
    if "administrators group name" in lower_log and re.search(r'\]:\s*$', log):
        shell.send("kladmins\n")
        log = ""
        print("\n[AUTO-SENT ADMIN GROUP: kladmins]")
        time.sleep(1)
        continue

    # KSC Administrator account name
    if "name of the administrator account" in lower_log and re.search(r'\]:\s*$', log):
        shell.send("KLAdmins\n")
        log = ""
        print("\n[AUTO-SENT KSC ADMIN USER: KLAdmins]")
        time.sleep(1)
        continue

    # KSC Administrator account password
    if "enter the password of ksc administrator account:" in lower_log and log.endswith(": "):
        shell.send("Ksc@2026\n")
        log = ""
        print("\n[AUTO-SENT KSC ADMIN PASS: ******]")
        time.sleep(1.5)
        continue

    # Confirm the password of KSC administrator account
    if "confirm the password" in lower_log and log.endswith(": "):
        shell.send("Ksc@2026\n")
        log = ""
        print("\n[AUTO-SENT CONFIRM PASS: ******]")
        time.sleep(1.5)
        continue

    # If the setup has completed successfully
    if "completed successfully" in lower_log or "concluída com êxito" in lower_log or "concluída com sucesso" in lower_log or "[root@kscserver ~]#" in log:
        print("\nWizard completed/terminated.")
        break

print("\nFinal run_postinstall execution log:")
print(log)

client.close()
