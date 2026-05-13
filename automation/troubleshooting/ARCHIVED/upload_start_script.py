import paramiko
import os
import sys

def upload_start_script(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        local_path = r'c:\Antigravity\ksc-deployment-runbook\scripts\start_console.py'
        remote_path = '/var/opt/kaspersky/ksc-web-console/start_console.py'

        print(f"--- Uploading {local_path} ---")
        sftp = client.open_sftp()
        sftp.put(local_path, '/tmp/start_console.py')
        sftp.close()

        print(f"--- Moving to {remote_path} ---")
        cmd = f'echo "{password}" | sudo -S mv /tmp/start_console.py {remote_path} && ' \
              f'echo "{password}" | sudo -S chown root:root {remote_path} && ' \
              f'echo "{password}" | sudo -S chmod 755 {remote_path}'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdout.read() # wait

        # Verify
        stdin, stdout, stderr = client.exec_command(f'ls -l {remote_path}')
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    upload_start_script(host, user, password)
