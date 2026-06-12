import paramiko
import os
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
        print("Connected.")

        # Run id kscadmin
        stdin, stdout, stderr = client.exec_command("id kscadmin")
        print("id kscadmin STDOUT:", stdout.read().decode("utf-8").strip())
        print("id kscadmin STDERR:", stderr.read().decode("utf-8").strip())

        # Run getent passwd kscadmin
        stdin, stdout, stderr = client.exec_command("getent passwd kscadmin")
        print("getent passwd kscadmin:", stdout.read().decode("utf-8").strip())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
