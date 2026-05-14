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
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        stdin.write(password + '\n')
        stdin.flush()
        out = stdout.read().decode('utf-8', errors='ignore')
        if out: print(out.encode('ascii', 'backslashreplace').decode('ascii'))
    client.close()

secrets = vault.decrypt_secrets()

env_content = f"""logsDir=server/logs/
logsFilesTtl=604800000
FEATURE_MESSAGE_BROKER_TYPE=nats
NATS_ADDRESS=127.0.0.1
NATS_PORT=4222
NODE_ENV=production
NODE_SERVER_PORT=8080
KSC_SERVER=127.0.0.1
KSC_PORT=13299
"""

service_content = f"""[Unit]
Description=Kaspersky Security Center Web Console
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/opt/kaspersky/ksc-web-console
Environment=NODE_ENV=production
Environment=FEATURE_MESSAGE_BROKER_TYPE=nats
Environment=NATS_ADDRESS=127.0.0.1
Environment=NATS_PORT=4222
Environment=NODE_SERVER_PORT=8080
Environment=NODE_EXTRA_CA_CERTS=/var/opt/kaspersky/ksc-web-console/ksc_server.pem
ExecStart=/var/opt/kaspersky/ksc-web-console/node /var/opt/kaspersky/ksc-web-console/index.js
Restart=always

[Install]
WantedBy=multi-user.target
"""

commands = [
    f"echo '{env_content}' | sudo tee /var/opt/kaspersky/ksc-web-console/.env",
    f"echo '{service_content}' | sudo tee /etc/systemd/system/ksc-web-console.service",
    "systemctl daemon-reload",
    "systemctl restart ksc-web-console"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], commands)
