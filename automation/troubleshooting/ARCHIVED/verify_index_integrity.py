import paramiko
import os
import sys


def verify_file_integrity(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target = "/var/opt/kaspersky/ksc-web-console/server/index.js"
        print(f"--- Verifying {target} ---")

        # RPM Verify
        stdin, stdout, stderr = client.exec_command(f"sudo -S rpm -Vf {target}")
        stdin.write(password + "\n")
        stdin.flush()
        print("RPM Verify output:")
        print(stdout.read().decode("utf-8"))

        # MD5
        stdin, stdout, stderr = client.exec_command(f"md5sum {target}")
        print("MD5sum output:")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    verify_file_integrity(host, user, password)
