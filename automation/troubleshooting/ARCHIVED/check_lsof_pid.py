import paramiko
import os
import sys

def check_lsof_pid(host, user, password, pid):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Lsof
        print(f"--- Lsof for PID {pid} ---")
        stdin, stdout, stderr = client.exec_command(f"sudo -S lsof -p {pid} | grep log")
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    pid = "229219"

    check_lsof_pid(host, user, password, pid)
