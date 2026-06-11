import paramiko
import os
import sys
import json


def update_config_structure(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_file = "/var/opt/kaspersky/ksc-web-console/server/config.json"
        print(f"--- Fixing structure in {target_file} ---")

        # Read current config
        stdin, stdout, stderr = client.exec_command(f"cat {target_file}")
        config_content = stdout.read().decode("utf-8")
        config = json.loads(config_content)

        # Correct openAPIServers structure
        if isinstance(config.get("openAPIServers"), list):
            servers = config["openAPIServers"]
            config["openAPIServers"] = {
                "pools": [{"id": "default", "servers": servers}]
            }

        # Ensure db path
        if "db" not in config:
            config["db"] = {"path": "server/db/db.json"}

        # Write back
        new_content = json.dumps(config, indent=4)

        # Upload via SFTP
        sftp = client.open_sftp()
        with sftp.file("/tmp/config.json", "w") as f:
            f.write(new_content)
        sftp.close()

        # Move to final location
        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/config.json {target_file}'
        )
        client.exec_command(
            f'echo "{password}" | sudo -S chown root:root {target_file}'
        )

        print("Config structure fixed successfully.")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    update_config_structure(host, user, password)
