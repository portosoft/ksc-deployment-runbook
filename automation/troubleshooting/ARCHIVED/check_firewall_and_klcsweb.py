import paramiko
import os
import sys


def check_firewall_and_klcsweb(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check Firewall
        print("--- Firewall Status ---")
        stdin, stdout, stderr = client.exec_command("sudo -S firewall-cmd --list-all")
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # Check klcsweb process
        print("--- klcsweb process info ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep klcsweb | grep -v grep"
        )
        print(stdout.read().decode("utf-8"))

        # Check where klcsweb is installed
        print("--- klcsweb binary path ---")
        stdin, stdout, stderr = client.exec_command("which klcsweb")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_firewall_and_klcsweb(host, user, password)
