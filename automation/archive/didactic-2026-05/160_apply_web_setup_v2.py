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
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

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
        print("New setup config:")
        print(config_str)

        # Upload
        sftp = client.open_sftp()
        with sftp.file("/tmp/ksc-web-console-setup-accepted.json", "w") as f:
            f.write(config_str)
        sftp.close()
        print("Uploaded setup JSON.")

        # Run setup inside sudo bash
        print("Running Web Console setup.js...")
        cmd = "sudo -S bash -c 'cd /var/opt/kaspersky/ksc-web-console && ./node setup.js /tmp/ksc-web-console-setup-accepted.json'"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()
        print(f"Setup exit code: {exit_code}")
        print("--- SETUP STDOUT ---")
        print(out)
        print("--- SETUP STDERR ---")
        print(err)

        # Restart service
        print("Restarting ksc-web-console service...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart ksc-web-console"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read()  # Wait for completion

        # Check status
        stdin, stdout, stderr = client.exec_command("systemctl status ksc-web-console")
        print("--- status ---")
        print(
            stdout.read()
            .decode("utf-8", errors="replace")
            .encode("ascii", errors="replace")
            .decode("ascii")
        )

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
