import paramiko
import os
import sys
import json


def phase_3_apply_config(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        config_data = {
            "address": "0.0.0.0",
            "port": 8080,
            "trustedCertificate": "",
            "defaultLanguageId": "pt-BR",
            "openAPIServers": [
                {
                    "address": "kscserver.tail8b9ae.ts.net",
                    "port": 13000,
                    "openApiPort": 13299,
                }
            ],
        }

        json_str = json.dumps(config_data, indent=2)
        target_path = "/var/opt/kaspersky/ksc-web-console/server/config.json"

        print(f"--- 3.2 Applying config to {target_path} ---")
        client.exec_command(f"echo '{json_str}' > /tmp/config.json")
        stdin, stdout, stderr = client.exec_command(
            f"sudo -S cp /tmp/config.json {target_path}"
        )
        stdin.write(password + "\n")
        stdin.flush()

        # Verify
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {target_path}")
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_3_apply_config(host, user, password)
