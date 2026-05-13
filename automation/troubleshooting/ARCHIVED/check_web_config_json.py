import paramiko
import os
import sys

def check_web_config_json(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check for the setup JSON file
        print("--- Checking for /etc/ksc-web-console-setup.json ---")
        stdin, stdout, stderr = client.exec_command("ls -l /etc/ksc-web-console-setup.json")
        print(stdout.read().decode('utf-8'))

        # Check for any other JSON in /etc/
        print("--- Searching for any ksc-web-console JSON in /etc/ ---")
        stdin, stdout, stderr = client.exec_command("ls /etc/*ksc-web-console* 2>/dev/null")
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_web_config_json(host, user, password)
