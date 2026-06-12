import paramiko
import os
import sys


def check_service_status_safe(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check service status
        print("--- KSCWebConsole.service status ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl status KSCWebConsole.service"
        )
        stdin.write(password + "\n")
        stdin.flush()
        out = stdout.read().decode("utf-8", errors="replace")
        print(out.encode("ascii", "ignore").decode("ascii"))

        # Check journalctl
        print("--- KSCWebConsole.service journalctl ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S journalctl -u KSCWebConsole.service -n 50"
        )
        stdin.write(password + "\n")
        stdin.flush()
        out = stdout.read().decode("utf-8", errors="replace")
        print(out.encode("ascii", "ignore").decode("ascii"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_service_status_safe(host, user, password)
