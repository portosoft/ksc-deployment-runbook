import paramiko
import os
import sys


def check_eaddrinuse_post_fix(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check for EADDRINUSE
        print("--- Checking for EADDRINUSE after fix ---")
        cmd = "sudo -S grep 'EADDRINUSE' /var/opt/kaspersky/ksc-web-console/logs/KSC-Web-Console-server.***REMOVED***.2026-05-09.log | tail -n 5"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # Check active ports
        print("--- All Listening Ports (Raw) ---")
        stdin, stdout, stderr = client.exec_command("sudo -S ss -tulpn")
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

    check_eaddrinuse_post_fix(host, user, password)
