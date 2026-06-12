import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password)

    sftp = client.open_sftp()
    remote_path = "/tmp/ksc-ca-for-browser.crt"
    local_path = "scratch/ksc-ca-for-browser.crt"

    print(f"Downloading {remote_path} to {local_path}...")
    sftp.get(remote_path, local_path)
    print("Download complete.")

    sftp.close()
    client.close()

if __name__ == "__main__":
    main()
