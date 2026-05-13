import paramiko
import os
import sys

def grep_web_console_scripts(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Grep for Web Console in setup scripts
        print("--- Searching for 'Web Console' in .pl scripts ---")
        cmd = "grep -i 'Web Console' /opt/kaspersky/ksc64/lib/bin/setup/*.pl"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    grep_web_console_scripts(host, user, password)
