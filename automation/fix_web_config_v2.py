import sys
import os
import paramiko
import json

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
        err = stderr.read().decode('utf-8', errors='ignore')
        if out: print(out.encode('ascii', 'backslashreplace').decode('ascii'))
        if err and "sudo: a senha" not in err: print(err.encode('ascii', 'backslashreplace').decode('ascii'))
    client.close()

secrets = vault.decrypt_secrets()

# We will read the config, modify it in Python, and push it back
def get_config(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)
    stdin, stdout, stderr = client.exec_command('cat /var/opt/kaspersky/ksc-web-console/server/config.json')
    data = stdout.read().decode()
    client.close()
    return json.loads(data)

config = get_config(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'])

# Replace all placeholders
fqdn = secrets['KSC_FQDN']
config['port'] = 8080
config['host'] = fqdn
config['cloudConsoleAddress'] = fqdn
config['socketUrl'] = f"//{fqdn}:8080"
config['trusted_cert'] = "BD6639623F83B1BD3019D4F3336521409F80710D37A6459DC259E726549F9333"  # pragma: allowlist secret

if 'openAPIServers' in config and 'pools' in config['openAPIServers']:
    for pool in config['openAPIServers']['pools']:
        pool['name'] = fqdn
        for srv in pool['servers']:
            srv['address'] = fqdn
            srv['port'] = 13000
            srv['openApiPort'] = 13299
            if 'name' in srv: srv['name'] = fqdn

# Add logger if missing
if 'logger' not in config:
    config['logger'] = {
        "level": "info",
        "path": "server/logs/"
    }

# Ensure production is string "true"
config['production'] = "true"

commands = [
    "mkdir -p /var/opt/kaspersky/ksc-web-console/server/logs",
    "mv /tmp/config.json.new /var/opt/kaspersky/ksc-web-console/server/config.json",
    "systemctl restart ksc-web-console",
    "sleep 5",
    "systemctl status ksc-web-console --no-pager | head -n 15"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], commands,
        upload_file={'local': 'config.json.tmp', 'remote': '/tmp/config.json.new', 'content': json.dumps(config, indent=2)})
