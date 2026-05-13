import paramiko
import os
import sys

def verify_index_clean(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target = '/var/opt/kaspersky/ksc-web-console/server/index.js'
        print(f"--- Final Verify {target} ---")

        stdin, stdout, stderr = client.exec_command(f'sudo -S rpm -Vf {target}')
        stdin.write(password + '\n')
        stdin.flush()
        print("RPM Verify:")
        print(stdout.read().decode('utf-8'))

        stdin, stdout, stderr = client.exec_command(f'md5sum {target}')
        print("MD5sum:")
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    verify_index_clean(host, user, password)
