import paramiko
import os
import sys
import time


def phase_4_startup(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 4.1 Start service
        print("--- 4.1 Starting KSCWebConsole.service ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl start KSCWebConsole.service"
        )
        stdin.write(password + "\n")
        stdin.flush()
        time.sleep(10)

        print("--- 4.1 Service Status ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl status KSCWebConsole.service"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # 4.2 Monitor journal
        print("--- 4.2 Journal Logs (Last 100) ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S journalctl -u KSCWebConsole.service --no-pager -n 100"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # 4.3 Check port 8080
        print("--- 4.3 Curl Test Port 8080 ---")
        stdin, stdout, stderr = client.exec_command(
            'curl -k https://127.0.0.1:8080 -o /dev/null -w "%{http_code}" 2>/dev/null'
        )
        print(f"HTTP Code: {stdout.read().decode('utf-8')}")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_4_startup(host, user, password)
