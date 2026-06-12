import paramiko
import os
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

        sftp = client.open_sftp()
        sftp.get("/var/opt/kaspersky/ksc-web-console/setup.js", "scratch/setup.js")
        sftp.close()
        print("Successfully downloaded setup.js to scratch/setup.js")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
