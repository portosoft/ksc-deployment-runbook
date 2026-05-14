import sys
import os
import paramiko
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)

    print(f"Executing: {command}")
    stdin, stdout, stderr = client.exec_command(f"sudo -S {command}")
    stdin.write(password + '\n')
    stdin.flush()

    start_time = time.time()
    while time.time() - start_time < 60:
        line = stdout.readline()
        if not line:
            break
        if "Attempt to write logs with no transports" in line:
            continue
        print(line.strip())
        if "Listening on" in line:
            print("MATCH FOUND!")
            break

    client.close()

secrets = vault.decrypt_secrets()

cmd = "bash -c 'cd /var/opt/kaspersky/ksc-web-console && ./node index.js'"
run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], cmd)
