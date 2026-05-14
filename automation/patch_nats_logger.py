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

# Patching to remove the Cyrillic 'a' (M-PM-0 in cat -v) and add more logging
# We'll use sed to replace it.
# The original line: this.logger.log(`Start create \u0430 new connection, (attempt #${reconnectCounter})`);
# In UTF-8, \u0430 is 0xd0 0xb0.

cmds = [
    "sed -i 's/Start create .* new connection/Start create a new connection/g' /var/opt/kaspersky/ksc-web-console/node_modules/@kl/app-components-connector/lib/nats/connection-creator.js",
    "sed -i '/NATS Connection created/a \\                    this.logger.log(\"NATS Connection resolved successfully\");' /var/opt/kaspersky/ksc-web-console/node_modules/@kl/app-components-connector/lib/nats/connection-creator.js",
    "systemctl restart ksc-web-console"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], cmds)
