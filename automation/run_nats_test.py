import sys
import os
import paramiko

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, commands, upload_file=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)

    if upload_file:
        sftp = client.open_sftp()
        sftp.put(upload_file['local'], upload_file['remote'])
        sftp.close()

    for cmd in commands:
        print(f"--- {cmd} ---")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='ignore')
        if out: print(out.encode('ascii', 'backslashreplace').decode('ascii'))
        err = stderr.read().decode('utf-8', errors='ignore')
        if err: print(err.encode('ascii', 'backslashreplace').decode('ascii'))
    client.close()

secrets = vault.decrypt_secrets()

cmds = [
    "export NODE_PATH=/var/opt/kaspersky/ksc-web-console/node_modules; /var/opt/kaspersky/ksc-web-console/node /tmp/test_nats.js"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], cmds,
        upload_file={'local': 'automation/test_nats_node.js', 'remote': '/tmp/test_nats.js'})
