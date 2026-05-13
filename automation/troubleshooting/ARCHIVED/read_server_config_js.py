import paramiko
import os
import sys

def read_server_config_js(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read server/config.js
        print("--- Reading server/config.js ---")
        stdin, stdout, stderr = client.exec_command("sudo -S cat /var/opt/kaspersky/ksc-web-console/server/config.js")
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    read_server_config_js(host, user, password)
