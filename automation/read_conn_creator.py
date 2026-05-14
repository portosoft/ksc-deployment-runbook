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
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='ignore')
        if out: print(out.encode('ascii', 'backslashreplace').decode('ascii'))
    client.close()

secrets = vault.decrypt_secrets()

cmds = [
    "cat /var/opt/kaspersky/ksc-web-console/node_modules/@kl/app-components-connector/lib/nats/connection-creator.js"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], cmds)
