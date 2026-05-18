import paramiko
import os
import sys


def fix_start_script(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_path = "/var/opt/kaspersky/ksc-web-console/start-console.sh"
        print(f"--- Fixing {target_path} ---")

        # Use sed to add ./ before pm.config.js
        cmd = f'sudo -S sed -i "s/pm.config.js/.\/pm.config.js/" {target_path}'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        # Verify
        stdin, stdout, stderr = client.exec_command(f"cat {target_path}")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    fix_start_script(host, user, password)
