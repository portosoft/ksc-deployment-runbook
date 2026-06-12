import paramiko
import os
import sys


def phase_1_audit_refined(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 1.1 RPM Verify (filtered)
        print("--- 1.1 RPM Verify (Filtered for S, M, 5) ---")
        stdin, stdout, stderr = client.exec_command(
            'rpm -V ksc-web-console | grep -E "^[SM5]{1,8}"'
        )
        print(stdout.read().decode("utf-8"))

        # 1.3 Config JSON
        print("--- 1.3 Config JSON content ---")
        stdin, stdout, stderr = client.exec_command(
            'sudo -S find /etc/kaspersky /var/opt/kaspersky -name "config.json"'
        )
        stdin.write(password + "\n")
        stdin.flush()
        paths = stdout.read().decode("utf-8").splitlines()

        for path in paths:
            print(f"File: {path}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S cat {path}")
            stdin.write(password + "\n")
            stdin.flush()
            print(stdout.read().decode("utf-8"))
            print("---")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_1_audit_refined(host, user, password)
