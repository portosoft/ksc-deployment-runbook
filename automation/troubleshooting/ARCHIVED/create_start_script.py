import paramiko
import os
import sys


def create_start_script(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        script_content = """#!/bin/bash
export FEATURE_MESSAGE_BROKER_TYPE=nats
export NATS_ADDRESS=127.0.0.1
export NATS_PORT=4222
export NSQ_HOST=127.0.0.1
export NSQ_PORT=4222

cd /var/opt/kaspersky/ksc-web-console
./node pm.js pm.config.js
"""

        target_path = "/var/opt/kaspersky/ksc-web-console/start-console.sh"
        print(f"--- Creating {target_path} ---")

        client.exec_command(f'echo "{script_content}" > /tmp/start-console.sh')
        stdin, stdout, stderr = client.exec_command(
            f"sudo -S mv /tmp/start-console.sh {target_path}"
        )
        stdin.write(password + "\n")
        stdin.flush()

        stdin, stdout, stderr = client.exec_command(f"sudo -S chmod +x {target_path}")
        stdin.write(password + "\n")
        stdin.flush()

        # Verify
        stdin, stdout, stderr = client.exec_command(f"ls -l {target_path}")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    create_start_script(host, user, password)
