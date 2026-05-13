import paramiko
import os
import sys

def capture_all_web_logs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # List all logs
        print("--- Listing logs ---")
        stdin, stdout, stderr = client.exec_command("ls -la /var/opt/kaspersky/ksc-web-console/logs/")
        print(stdout.read().decode('utf-8'))

        # Read each log
        print("--- Reading logs ---")
        stdin, stdout, stderr = client.exec_command("ls /var/opt/kaspersky/ksc-web-console/logs/*.log")
        log_files = stdout.read().decode('utf-8').splitlines()

        for log_file in log_files:
            print(f"--- Log: {log_file} ---")
            stdin, stdout, stderr = client.exec_command(f"sudo -S tail -n 50 {log_file}")
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

    capture_all_web_logs(host, user, password)
