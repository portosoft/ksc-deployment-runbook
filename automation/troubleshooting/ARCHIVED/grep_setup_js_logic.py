import paramiko
import os
import sys

def grep_setup_js_logic(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Grep for logic in setup.js
        cmds = [
            "grep -iE 'argv|args|process\.env' /var/opt/kaspersky/ksc-web-console/setup.js | head -n 50",
            "grep -iE 'config|json' /var/opt/kaspersky/ksc-web-console/setup.js | head -n 50"
        ]

        for cmd in cmds:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
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

    grep_setup_js_logic(host, user, password)
