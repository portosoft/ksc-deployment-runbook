import paramiko
import os
import sys

def deep_diagnose_access(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Diagnostics: Services, Ports, SELinux, Logs
        cmds = [
            "sudo systemctl list-units --type=service | grep -iE 'kl|kaspersky|ksc'",
            "sudo ss -tulpn",
            "getenforce",
            "sudo journalctl -u ksc-web-console -n 50 --no-pager"
        ]

        for cmd in cmds:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
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

    if not all([host, user, password]):
        print("Missing environment variables.")
        sys.exit(1)

    deep_diagnose_access(host, user, password)
