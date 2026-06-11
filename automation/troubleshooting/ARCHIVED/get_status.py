import paramiko
import os
import sys


def get_service_status(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        print("--- systemctl status ksc-web-console.service ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl status ksc-web-console.service"
        )
        stdin.write(password + "\n")
        stdin.flush()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        with open(
            r"c:\Antigravity\ksc-deployment-runbook\scripts\service_status.txt",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(out)
            f.write("\n--- STDERR ---\n")
            f.write(err)
        print("Status saved to scripts/service_status.txt")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    get_service_status(host, user, password)
