import paramiko
import os
import sys


def search_error_trigger(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for error string
        print("--- Searching for error trigger ---")
        cmd = "sudo -S grep -ri 'Incorrect configuration' /var/opt/kaspersky/ksc-web-console/server/ | head -n 20"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # Search for 'servers-selection' or similar
        print("--- Searching for server selection logic ---")
        cmd = "sudo -S grep -ri 'serverSelection' /var/opt/kaspersky/ksc-web-console/server/ | head -n 20"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_error_trigger(host, user, password)
