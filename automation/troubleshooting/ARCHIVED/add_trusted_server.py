import paramiko
import os
import sys
import json
import uuid


def add_trusted_server(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 1. Read existing config.json
        print("--- Reading current config.json ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /var/opt/kaspersky/ksc-web-console/server/config.json"
        )
        stdin.write(password + "\n")
        stdin.flush()
        config_content = stdout.read().decode("utf-8")

        # Strip sudo prompt if present
        if "[sudo]" in config_content:
            config_content = config_content.split("\n", 1)[1]

        config = json.loads(config_content)

        # 2. Add server to pool
        print("--- Adding Administration Server to pool ---")
        server_id = str(uuid.uuid4())
        new_server = {
            "id": server_id,
            "address": "127.0.0.1",
            "port": 13299,
            "isIAM": False,
            "useSsl": True,
        }

        if not config["openAPIServers"]["pools"][0]["servers"]:
            config["openAPIServers"]["pools"][0]["servers"].append(new_server)

        new_config_json = json.dumps(config, indent=2)

        # 3. Write new config.json
        print("--- Writing updated config.json ---")
        client.exec_command(f"echo '{new_config_json}' > /tmp/config_trusted.json")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cp /tmp/config_trusted.json /var/opt/kaspersky/ksc-web-console/server/config.json"
        )
        stdin.write(password + "\n")
        stdin.flush()

        # 4. Restart Services
        print("--- Restarting Web Console Services ---")
        client.exec_command(
            "sudo -S systemctl restart KSCWebConsole.service KSCSvcWebConsole.service"
        )
        stdin.write(password + "\n")
        stdin.flush()

        print("Done!")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    add_trusted_server(host, user, password)
