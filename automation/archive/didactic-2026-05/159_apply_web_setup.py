import paramiko
import os
import json
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    # Read original JSON format from the remote server
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Read the current configuration JSON
        stdin, stdout, stderr = client.exec_command(
            "cat /etc/ksc-web-console-setup.json"
        )
        original_json_str = stdout.read().decode("utf-8")

        try:
            config = json.loads(original_json_str)
        except Exception as e:
            print(f"Error parsing JSON: {e}. Falling back to default structure.")
            config = {
                "address": "kscserver.tail8b9ae.ts.net",
                "port": 8080,
                "trusted_cert": "",
                "trusted_cert_key": "",
                "defaultLanguageId": "pt-BR",
                "openAPIServers": [
                    {
                        "address": "kscserver.tail8b9ae.ts.net",
                        "port": 13000,
                        "openApiPort": 13299,
                    }
                ],
            }

        # Add EULA acceptance
        config["acceptEula"] = True

        # Format as string
        config_str = json.dumps(config, indent=2)
        print("New config:")
        print(config_str)

        # Upload configuration to a temporary path on the remote server
        print(
            "Uploading new configuration to /tmp/ksc-web-console-setup-accepted.json..."
        )
        sftp = client.open_sftp()
        with sftp.file("/tmp/ksc-web-console-setup-accepted.json", "w") as f:
            f.write(config_str)
        sftp.close()

        # Run setup.js with the temporary configuration path
        print("Running Web Console setup.js...")
        cmd = "cd /var/opt/kaspersky/ksc-web-console && sudo -S ./node setup.js /tmp/ksc-web-console-setup-accepted.json"
        stdin, stdout, stderr = client.exec_command(cmd)

        # Send sudo password
        stdin.write(password + "\n")
        stdin.flush()

        # Read outputs
        out = stdout.read().decode("utf-8")
        err = stderr.read().decode("utf-8")
        exit_code = stdout.channel.recv_exit_status()

        print(f"Exit code: {exit_code}")
        print("--- STDOUT ---")
        print(out)
        print("--- STDERR ---")
        print(err)

        # Let's check the systemctl status of ksc-web-console
        print("Checking service status...")
        stdin, stdout, stderr = client.exec_command("systemctl status ksc-web-console")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
