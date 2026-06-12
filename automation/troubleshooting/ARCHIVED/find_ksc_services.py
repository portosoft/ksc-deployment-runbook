import paramiko
import os
import sys


def find_ksc_services(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # List services
        print("--- KSC Services ---")
        stdin, stdout, stderr = client.exec_command(
            "systemctl list-units --type=service --all | grep -i ksc"
        )
        print(stdout.read().decode("utf-8"))

        # Find unit files
        print("--- Unit Files ---")
        stdin, stdout, stderr = client.exec_command(
            'find /etc/systemd/system /usr/lib/systemd/system -name "*ksc*" -o -name "*KSC*"'
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    find_ksc_services(host, user, password)
