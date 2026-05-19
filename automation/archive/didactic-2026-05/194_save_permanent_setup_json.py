import paramiko
import os
import json
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Build the correct setup JSON structure
        config = {
            "acceptEula": True,
            "address": "kscserver.tail8b9ae.ts.net",
            "port": 8080,
            "defaultLanguageId": "pt-BR",
            "trusted": {
                "kscserver.tail8b9ae.ts.net": {
                    "kscHost": "127.0.0.1",
                    "kscPort": 13299,
                    "kscCertPath": "/var/opt/kaspersky/ksc-web-console/KLRootCA.crt",
                }
            },
        }

        config_str = json.dumps(config, indent=2)

        # Upload to temp path
        sftp = client.open_sftp()
        with sftp.file("/tmp/ksc-web-console-setup.json", "w") as f:
            f.write(config_str)
        sftp.close()
        print("Uploaded permanent setup JSON to /tmp.")

        # Move to /etc/ksc-web-console-setup.json via sudo
        print("Moving to /etc/ksc-web-console-setup.json...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cp /tmp/ksc-web-console-setup.json /etc/ksc-web-console-setup.json"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read()  # Wait for completion

        # Check permissions
        stdin, stdout, stderr = client.exec_command(
            "ls -la /etc/ksc-web-console-setup.json"
        )
        print("File details:")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
