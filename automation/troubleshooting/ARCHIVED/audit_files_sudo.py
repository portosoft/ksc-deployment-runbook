import paramiko
import os
import sys

def audit_files_sudo(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        files = [
            '/var/opt/kaspersky/ksc-web-console/server/index.js',
            '/var/opt/kaspersky/ksc-web-console/server/core/server.js',
            '/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js'
        ]

        print("--- MD5SUM of target files (SUDO) ---")
        for f in files:
            stdin, stdout, stderr = client.exec_command(f'sudo -S md5sum {f}')
            stdin.write(password + '\n')
            stdin.flush()
            print(stdout.read().decode('utf-8').strip())

        print("\n--- RPM Verify of target files (SUDO) ---")
        for f in files:
            stdin, stdout, stderr = client.exec_command(f'sudo -S rpm -V ksc-web-console | grep "{f}"')
            stdin.write(password + '\n')
            stdin.flush()
            out = stdout.read().decode('utf-8').strip()
            if out:
                print(out)
            else:
                print(f"{f}: OK (according to RPM)")

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    audit_files_sudo(host, user, password)
