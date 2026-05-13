import paramiko
import os
import sys

def find_iam_config(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        print("--- Searching for ksciam/kluser configs ---")
        # Search in /etc and /var/opt/kaspersky
        cmd = 'sudo -S find /etc/ /var/opt/kaspersky/ -type f \( -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.conf" \) -exec grep -l "ksciam" {} +'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + '\n')
        stdin.flush()

        results = stdout.read().decode('utf-8').splitlines()
        for r in results:
            print(f"Found: {r}")
            # Try to peek into it
            # client.exec_command(f'sudo -S cat {r} | grep -C 5 "kluser"')

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    find_iam_config(host, user, password)
