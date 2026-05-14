import sys
import os
import paramiko

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)

    secrets = vault.decrypt_secrets()
    sensitive_vals = [str(v) for v in secrets.values()]

    for cmd in commands:
        masked_cmd = cmd
        for val in sensitive_vals:
            if val and len(val) > 3:
                masked_cmd = masked_cmd.replace(val, '***REMOVED***')
        print(f"Executing: {masked_cmd}")
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        stdin.write(password + '\n')
        stdin.flush()
        out = stdout.read().decode('utf-8', errors='ignore')
        if out: print(out.encode('ascii', 'backslashreplace').decode('ascii'))
    client.close()

secrets = vault.decrypt_secrets()

# Generate self-signed cert
cert_cmds = [
    "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /var/opt/kaspersky/ksc-web-console/web-server.key -out /var/opt/kaspersky/ksc-web-console/web-server.crt -subj '/CN=" + secrets['KSC_FQDN'] + "'",
    "chown root:root /var/opt/kaspersky/ksc-web-console/web-server.*",
    "chmod 600 /var/opt/kaspersky/ksc-web-console/web-server.key",
    "systemctl restart ksc-web-console",
    "sleep 5",
    "systemctl status ksc-web-console --no-pager | head -n 10"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], cert_cmds)
