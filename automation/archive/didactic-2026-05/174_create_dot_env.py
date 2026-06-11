import paramiko
import os
import sys
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("--- Connected successfully to remote server ---")

        dot_env_content = """NODE_ENV=production
FEATURE_MESSAGE_BROKER_TYPE=nats
NATS_ADDRESS=127.0.0.1
NATS_PORT=4222
NODE_SERVER_PORT=8080
NODE_EXTRA_CA_CERTS=/var/opt/kaspersky/ksc-web-console/ksc_root_ca.pem
NODE_TLS_REJECT_UNAUTHORIZED=0
skipTrustedCertificatesCheck=true
logsDir=logs
logsFilesTtl=2592000000
verboseOutput=true
"""

        # Upload via SFTP to /tmp/.env
        sftp = client.open_sftp()
        with sftp.open("/tmp/.env", "w") as f:
            f.write(dot_env_content)
        sftp.close()
        print("Uploaded .env to /tmp/.env")

        # Move to /var/opt/kaspersky/ksc-web-console/.env with sudo
        cmds = [
            "sudo -S mv /tmp/.env /var/opt/kaspersky/ksc-web-console/.env",
            "sudo -S chown root:root /var/opt/kaspersky/ksc-web-console/.env",
            "sudo -S chmod 644 /var/opt/kaspersky/ksc-web-console/.env",
            "sudo -S cat /var/opt/kaspersky/ksc-web-console/.env",
            "sudo -S systemctl daemon-reload",
            "sudo -S systemctl restart ksc-web-console",
            "sudo -S systemctl status ksc-web-console --no-pager",
            "sudo -S ss -tulpn | grep 8080",
        ]

        for cmd in cmds:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            out_bytes = stdout.read()
            err_bytes = stderr.read()

            # Print safely
            out_str = out_bytes.decode("utf-8", errors="replace").replace("\u25cf", "*")
            err_str = err_bytes.decode("utf-8", errors="replace").replace("\u25cf", "*")
            sys.stdout.buffer.write(
                out_str.encode(sys.stdout.encoding or "utf-8", errors="replace") + b"\n"
            )
            sys.stderr.buffer.write(
                err_str.encode(sys.stderr.encoding or "utf-8", errors="replace") + b"\n"
            )

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
