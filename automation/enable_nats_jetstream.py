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

nats_conf = """port: 4222
monitor_port: 8222
jetstream: {
    store_dir: "/var/opt/kaspersky/ksc-web-console/nats-data"
}
"""

commands = [
    "mkdir -p /var/opt/kaspersky/ksc-web-console/nats-data",
    "chown root:root /var/opt/kaspersky/ksc-web-console/nats-data",
    f"echo '{nats_conf}' | sudo tee /var/opt/kaspersky/ksc-web-console/nats.conf",
    "systemctl restart ksc-web-console", # This should also restart NATS if it's managed by the same tool, but here I should restart nats-server.
    "pkill -9 nats-server", # Force restart nats-server if it's not a service.
    "nohup /var/opt/kaspersky/ksc-web-console/vendor/nats-server -c /var/opt/kaspersky/ksc-web-console/nats.conf > /var/opt/kaspersky/ksc-web-console/logs/nats.log 2>&1 &",
    "sleep 5",
    "systemctl restart ksc-web-console"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], commands)
