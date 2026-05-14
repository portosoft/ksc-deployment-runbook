import sys
import os
import paramiko

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)
    for cmd in commands:
        print(f"--- {cmd} ---")
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        stdin.write(password + '\n')
        stdin.flush()
        out = stdout.read().decode('utf-8', errors='ignore')
        if out: print(out.encode('ascii', 'backslashreplace').decode('ascii'))
    client.close()

secrets = vault.decrypt_secrets()

# Fetch cert from 13299 and save to /var/opt/kaspersky/ksc-web-console/ksc_server.pem
cmds = [
    "bash -c 'echo | openssl s_client -connect 127.0.0.1:13299 2>/dev/null | openssl x509 > /var/opt/kaspersky/ksc-web-console/ksc_server.pem'",
    "chown root:root /var/opt/kaspersky/ksc-web-console/ksc_server.pem",
    "chmod 644 /var/opt/kaspersky/ksc-web-console/ksc_server.pem"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], cmds)
