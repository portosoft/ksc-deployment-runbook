import paramiko
import os
import sys


def check_web_console_final(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check Final State
        print("--- Checking Web Console Final State ---")
        cmds = [
            "ls -l /var/opt/kaspersky/ksc-web-console/start-console.sh",
            "sudo -S systemctl status ksc-web-console",
            "sudo -S ss -tulpn | grep 8080",
            "sudo -S ss -tulpn | grep node",
        ]

        for cmd in cmds:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            if "sudo" in cmd:
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

    check_web_console_final(host, user, password)
