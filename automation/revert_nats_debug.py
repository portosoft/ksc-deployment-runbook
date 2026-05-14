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

cmds = [
    "sed -i 's/console.log(\"\[DEBUG-NATS\] \", /this.logger.log(/g' /var/opt/kaspersky/ksc-web-console/node_modules/@kl/app-components-connector/lib/nats/connection-creator.js",
    "sed -i 's/console.error(\"\[DEBUG-NATS-ERROR\] \", /this.logger.error(/g' /var/opt/kaspersky/ksc-web-console/node_modules/@kl/app-components-connector/lib/nats/connection-creator.js",
    "sed -i '/NATS Connection resolved successfully/d' /var/opt/kaspersky/ksc-web-console/node_modules/@kl/app-components-connector/lib/nats/connection-creator.js",
    "systemctl restart ksc-web-console"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], cmds)
