import paramiko
import os
import sys
import json

def update_config_localization(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_file = '/var/opt/kaspersky/ksc-web-console/server/config.json'
        print(f"--- Updating localization in {target_file} ---")

        # Read current config
        stdin, stdout, stderr = client.exec_command(f'cat {target_file}')
        config_content = stdout.read().decode('utf-8')
        config = json.loads(config_content)

        # Add localization if missing
        if "localization" not in config:
            config["localization"] = {
                "default": "en",
                "supported": [
                    "en", "de", "fr", "es", "it", "ja",
                    "zh-Hans", "zh-Hant", "ko", "pt-BR",
                    "ru", "pl", "tr", "cs", "ar"
                ]
            }

        # Write back
        new_content = json.dumps(config, indent=4)

        # Upload via SFTP
        sftp = client.open_sftp()
        with sftp.file('/tmp/config.json', 'w') as f:
            f.write(new_content)
        sftp.close()

        # Move to final location
        client.exec_command(f'echo "{password}" | sudo -S mv /tmp/config.json {target_file}')
        client.exec_command(f'echo "{password}" | sudo -S chown root:root {target_file}')

        print("Localization updated successfully.")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    update_config_localization(host, user, password)
