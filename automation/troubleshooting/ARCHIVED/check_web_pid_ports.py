import paramiko
import os
import sys


def check_web_pid_ports(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Get PID of node ./index.js
        print("--- Finding PID of node ./index.js ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep 'node ./index.js' | grep -v grep | awk '{print $2}'"
        )
        pid = stdout.read().decode("utf-8").strip()
        print(f"PID: {pid}")

        if pid:
            print(f"--- Checking ports for PID {pid} ---")
            stdin, stdout, stderr = client.exec_command(
                f"sudo -S ss -tulpn | grep {pid}"
            )
            stdin.write(password + "\n")
            stdin.flush()
            print(stdout.read().decode("utf-8"))

        # Try curl again
        print("--- Testing Curl on 8061 and 8060 ---")
        cmds = [
            "curl -Ik http://localhost:8061",
            "curl -Ik http://localhost:8060",
            "curl -Ik https://localhost:8061",
            "curl -Ik https://localhost:8060",
        ]
        for cmd in cmds:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode("utf-8"))
            print(stderr.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_web_pid_ports(host, user, password)
