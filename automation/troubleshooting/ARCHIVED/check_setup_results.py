import paramiko
import os
import sys

def check_setup_results(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check files
        print("--- Checking files ---")
        cmds = [
            "ls -l /var/opt/kaspersky/ksc-web-console/start-console.sh",
            "ls -l /etc/ksc-web-console.conf",
            "sudo -S systemctl status ksc-web-console",
            "sudo -S journalctl -u ksc-web-console -n 20 --no-pager"
        ]

        for cmd in cmds:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            if "sudo" in cmd:
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

    check_setup_results(host, user, password)
