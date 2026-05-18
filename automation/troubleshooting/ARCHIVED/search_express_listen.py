import paramiko
import os
import sys


def search_express_listen(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for listen calls
        print("--- Searching for '.listen(' in JS files ---")
        cmd = "grep -r '\.listen(' /var/opt/kaspersky/ksc-web-console/server/ | grep -v 'node_modules' | head -n 20"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        # Check index.js content
        print("--- Reading index.js ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /var/opt/kaspersky/ksc-web-console/index.js"
        )
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

    search_express_listen(host, user, password)
