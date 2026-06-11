import paramiko
import os
import sys


def find_web_setup(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Comprehensive search for setup scripts
        search_paths = [
            "rpm -ql ksc-web-console | grep -iE 'setup|install|config'",
            "find /opt/kaspersky /var/opt/kaspersky -name '*.sh' -o -name '*.pl'",
            "which ksc-web-console-setup",
            "ls -la /opt/kaspersky/",
        ]

        for cmd in search_paths:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
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

    if not all([host, user, password]):
        sys.exit(1)

    find_web_setup(host, user, password)
