import sys
import os
import paramiko

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, commands, upload_file=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)

    secrets = vault.decrypt_secrets()
    sensitive_vals = [str(v) for v in secrets.values()]

    if upload_file:
        sftp = client.open_sftp()
        with open(upload_file['local'], 'w') as f:
            f.write(upload_file['content'])
        sftp.put(upload_file['local'], upload_file['remote'])
        sftp.close()
        os.remove(upload_file['local'])

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

nats_config = """port: 4222
monitor_port: 8222
"""

commands = [
    "mv /tmp/nats.conf.new /var/opt/kaspersky/ksc-web-console/nats.conf",
    "chown root:root /var/opt/kaspersky/ksc-web-console/nats.conf",
    "systemctl restart ksc-nats",
    "systemctl restart ksc-web-console",
    "sleep 10",
    "ss -tlnp | grep -E '4222|8080'"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], commands,
        upload_file={'local': 'nats.conf.tmp', 'remote': '/tmp/nats.conf.new', 'content': nats_config})
