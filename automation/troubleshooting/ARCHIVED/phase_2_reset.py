import paramiko
import os
import sys
import time


def phase_2_reset(host, user, password, rpm_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 2.1 Remove package
        print(f"--- 2.1 Removing ksc-web-console ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S rpm -e ksc-web-console --nodeps"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))
        print(stderr.read().decode("utf-8"))

        # 2.2 Confirm removal
        print("--- 2.2 Confirming removal ---")
        stdin, stdout, stderr = client.exec_command("rpm -qi ksc-web-console")
        out = stdout.read().decode("utf-8")
        if "is not installed" in out or not out:
            print("Confirmed: Package removed.")
        else:
            print("Warning: Package might still be there.")
            print(out)

        # 2.3 Reinstall
        print(f"--- 2.3 Reinstalling from {rpm_path} ---")
        stdin, stdout, stderr = client.exec_command(f"sudo -S rpm -ivh {rpm_path}")
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))
        print(stderr.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    rpm_path = "/tmp/ksc-web-console-16.2.11309.x86_64.rpm"

    phase_2_reset(host, user, password, rpm_path)
