import paramiko
import os
import sys
import json


def run_web_console_setup_minimal(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=60)

        # Minimal JSON
        config = {"acceptEula": True, "address": "127.0.0.1", "port": "13299"}

        json_content = json.dumps(config)

        # Upload JSON
        print("--- Uploading setup-minimal.json ---")
        client.exec_command(f"echo '{json_content}' > /tmp/web-setup-minimal.json")

        # Run Setup
        print("--- Running setup.js minimal ---")
        cmd = "cd /var/opt/kaspersky/ksc-web-console && sudo -S ./node setup.js /tmp/web-setup-minimal.json"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print(f"STDOUT:\n{stdout.read().decode('utf-8')}")
        print(f"STDERR:\n{stderr.read().decode('utf-8')}")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    run_web_console_setup_minimal(host, user, password)
