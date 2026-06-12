import paramiko
import os
import sys


def check_start_script_fixed(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read the start-console.sh script
        print("--- Reading start-console.sh ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /var/opt/kaspersky/ksc-web-console/start-console.sh"
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

    check_start_script_fixed(host, user, password)
