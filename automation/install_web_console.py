import sys
import os
import paramiko
import json

# Add lib to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, commands, upload_file=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)

    if upload_file:
        sftp = client.open_sftp()
        with open(upload_file['local'], 'w') as f:
            f.write(upload_file['content'])
        sftp.put(upload_file['local'], upload_file['remote'])
        sftp.close()
        os.remove(upload_file['local'])

    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        stdin.write(password + '\n')
        stdin.flush()
        out = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')
        if out: print(out.encode('ascii', 'backslashreplace').decode('ascii'))
        if err and "sudo: a senha" not in err: print(err.encode('ascii', 'backslashreplace').decode('ascii'))
    client.close()

secrets = vault.decrypt_secrets()

# Phase 2: Web Console Setup JSON
web_setup = {
    "address": secrets['KSC_FQDN'],
    "port": 8080,
    "trusted_cert": "",
    "defaultLanguageId": "pt-BR",
    "openAPIServers": [
        {
            "address": secrets['KSC_FQDN'],
            "port": 13000,
            "openApiPort": 13299
        }
    ]
}

web_cmds = [
    "mv /tmp/ksc-web-console-setup.json /etc/ksc-web-console-setup.json",
    "rpm -ivh /tmp/ksc-web-console-16.2.11309.x86_64.rpm",
    # Create web admin user
    f"/opt/kaspersky/ksc64/sbin/kladduser -n KLAdmins -u ksc_admin -p '{secrets['KSC_PASS']}' -r Administrator",
    # Firewall
    "firewall-cmd --permanent --add-port=8080/tcp",
    "firewall-cmd --permanent --add-port=13000/tcp",
    "firewall-cmd --permanent --add-port=13299/tcp",
    "firewall-cmd --reload"
]

print("--- Installing Web Console ---")
run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], web_cmds,
        upload_file={'local': 'web_setup.tmp', 'remote': '/tmp/ksc-web-console-setup.json', 'content': json.dumps(web_setup, indent=2)})
