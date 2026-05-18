import paramiko
import os
import sys


def patch_nats_js(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        filepath = "/var/opt/kaspersky/ksc-web-console/node_modules/@kl/app-components-connector/lib/nats/connection-creator.js"
        print(f"--- Patching {filepath} ---")

        # Read the file
        sftp = client.open_sftp()
        with sftp.file(filepath, "r") as f:
            content = f.read().decode("utf-8", errors="ignore")

        # Replace the Cyrillic 'a' (\u0430) with standard 'a'
        # The line is: Start create а new connection
        new_content = content.replace("\u0430 new", "a new")

        # Also, let's fix any other potential Cyrillic characters in logs just in case
        # But for now, let's target the specific one we found.

        if content == new_content:
            print("No change detected. Trying byte-level replacement...")
            # Maybe it's encoded differently?
            # \u0430 in UTF-8 is \xd0\xb0
            new_content = content.replace("\xd0\xb0 new", "a new")

        with sftp.file("/tmp/connection-creator.js", "w") as f:
            f.write(new_content)
        sftp.close()

        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/connection-creator.js {filepath}'
        )

        # Force kill and restart
        print("--- Restarting all Node processes ---")
        client.exec_command(f'echo "{password}" | sudo -S pkill -9 -f node')
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )

        client.close()
        print("Patch applied and services restarted.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    patch_nats_js(host, user, password)
