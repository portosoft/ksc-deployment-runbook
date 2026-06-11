import paramiko
import os
import sys


def download_file(host, user, password, remote_path, local_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        client.close()
        print(f"File downloaded to {local_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    remote_path = "/var/opt/kaspersky/ksc-web-console/node_modules/@kl/app-components-connector/lib/nats/connection-creator.js"
    local_path = "c:\\Antigravity\\ksc-deployment-runbook\\automation\\troubleshooting\\connection-creator.js"

    download_file(host, user, password, remote_path, local_path)
