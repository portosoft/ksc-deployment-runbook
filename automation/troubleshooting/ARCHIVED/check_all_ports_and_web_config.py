import paramiko
import os
import sys


def check_all_ports_and_web_config(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check all ports
        print("--- All Listening Ports ---")
        stdin, stdout, stderr = client.exec_command("sudo -S ss -tulpn")
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # Check for 8080 in config.json
        print("--- Checking config.json for 8080 ---")
        stdin, stdout, stderr = client.exec_command(
            "grep '8080' /var/opt/kaspersky/ksc-web-console/server/config.json"
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_all_ports_and_web_config(host, user, password)
