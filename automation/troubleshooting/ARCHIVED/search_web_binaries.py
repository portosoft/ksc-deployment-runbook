import paramiko
import os
import sys


def search_web_binaries(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for any web-console binaries
        print("--- Searching for web-console binaries in /usr/bin ---")
        cmd = "ls /usr/bin/*web-console* 2>/dev/null"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        # Check /usr/sbin too
        print("--- Searching for web-console binaries in /usr/sbin ---")
        cmd = "ls /usr/sbin/*web-console* 2>/dev/null"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_web_binaries(host, user, password)
