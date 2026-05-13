import paramiko
import os
import sys

def read_setup_js(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read setup.js
        print("--- Reading setup.js ---")
        stdin, stdout, stderr = client.exec_command('cat /var/opt/kaspersky/ksc-web-console/setup.js')
        content = stdout.read().decode('utf-8', errors='ignore')

        with open(r'c:\Antigravity\ksc-deployment-runbook\scripts\setup_analyzed.js', 'w', encoding='utf-8') as f:
            f.write(content)

        print("File saved to scripts/setup_analyzed.js")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    read_setup_js(host, user, password)
