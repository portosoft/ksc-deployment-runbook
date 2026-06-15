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

        # Check date
        stdin, stdout, stderr = client.exec_command("date")
        print("Date on KSC server:", stdout.read().decode("utf-8").strip())

        # Check uptime of service
        stdin, stdout, stderr = client.exec_command("systemctl show ksc-web-console --property=ActiveEnterTimestamp")
        print("Service active timestamp:", stdout.read().decode("utf-8").strip())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
