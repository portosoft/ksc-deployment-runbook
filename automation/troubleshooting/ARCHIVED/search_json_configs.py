import paramiko
import os
import sys


def search_json_configs(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for any JSON config templates
        print("--- Searching for JSON config templates ---")
        cmd = (
            "sudo find /var/opt/kaspersky/ksc-web-console /opt/kaspersky -name '*.json'"
        )
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_json_configs(host, user, password)
