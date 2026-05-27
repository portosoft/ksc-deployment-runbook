import paramiko
import os
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

        sftp = client.open_sftp()
        files = sftp.listdir('/tmp/extracted_migrations/')

        targets = ["1756292315", "1756292317", "1756292320", "1756292321"]
        matching = [f for f in files if any(t in f for t in targets)]
        print("Matching files in /tmp/extracted_migrations/:")
        for m in sorted(matching):
            print(" -", m)

        sftp.close()
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
