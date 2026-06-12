import paramiko
import os
import sys


def check_web_install_log_fixed(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read the install log
        print("--- Reading install-patch-config.log ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /var/opt/kaspersky/ksc-web-console/logs/install-patch-config.log"
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

    check_web_install_log_fixed(host, user, password)
