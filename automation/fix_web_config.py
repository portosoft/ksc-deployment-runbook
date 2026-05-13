import sys
import os
import paramiko
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)
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

# Manual replacement of placeholders in config.json
fix_config_cmds = [
    f"sed -i 's/\\$web_console_address\\$/{secrets['KSC_FQDN']}/g' /var/opt/kaspersky/ksc-web-console/server/config.json",
    f"sed -i 's/\\$web_console_port\\$/8080/g' /var/opt/kaspersky/ksc-web-console/server/config.json",
    f"sed -i 's/\\$open_api_host\\$/{secrets['KSC_FQDN']}/g' /var/opt/kaspersky/ksc-web-console/server/config.json",
    f"sed -i 's/\\$open_api_port\\$/13000/g' /var/opt/kaspersky/ksc-web-console/server/config.json",
    "systemctl restart ksc-web-console",
    "sleep 5",
    "systemctl status ksc-web-console --no-pager | head -n 15"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], fix_config_cmds)
