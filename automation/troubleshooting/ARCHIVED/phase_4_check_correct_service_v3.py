import paramiko
import os
import sys


def phase_4_check_correct_service_v3(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 4.1 Status
        print("--- 4.1 ksc-web-console.service Status ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl status ksc-web-console.service"
        )
        stdin.write(password + "\n")
        stdin.flush()
        out = stdout.read().decode("utf-8", errors="ignore")
        print(out.encode("ascii", "ignore").decode("ascii"))

        # 4.2 Journal
        print("--- 4.2 Journal Logs (Last 50) ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S journalctl -u ksc-web-console.service --no-pager -n 50"
        )
        stdin.write(password + "\n")
        stdin.flush()
        out = stdout.read().decode("utf-8", errors="ignore")
        print(out.encode("ascii", "ignore").decode("ascii"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_4_check_correct_service_v3(host, user, password)
