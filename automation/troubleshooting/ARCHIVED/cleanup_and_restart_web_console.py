import paramiko
import os
import sys


def cleanup_and_restart_web_console(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 1. Stop all known services
        print("--- Stopping services ---")
        client.exec_command(
            "sudo -S systemctl stop KSCWebConsole.service KSCSvcWebConsole.service kliam_srv klnagent_srv kladminserver_srv"
        )
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl stop KSCWebConsole.service KSCSvcWebConsole.service"
        )
        stdin.write(password + "\n")
        stdin.flush()

        # 2. Kill all node processes
        print("--- Killing all node processes ---")
        stdin, stdout, stderr = client.exec_command("sudo -S killall -9 node")
        stdin.write(password + "\n")
        stdin.flush()

        # 3. Wait a bit
        import time

        time.sleep(5)

        # 4. Start services in order
        print("--- Starting services ---")
        services = [
            "kladminserver_srv",
            "klnagent_srv",
            "kliam_srv",
            "KSCSvcWebConsole.service",
            "KSCWebConsole.service",
        ]
        for svc in services:
            print(f"Starting {svc}...")
            stdin, stdout, stderr = client.exec_command(
                f"sudo -S systemctl start {svc}"
            )
            stdin.write(password + "\n")
            stdin.flush()
            time.sleep(2)

        # 5. Verify 8080
        print("--- Verifying port 8080 ---")
        stdin, stdout, stderr = client.exec_command("sudo -S ss -tulpn | grep 8080")
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

    cleanup_and_restart_web_console(host, user, password)
