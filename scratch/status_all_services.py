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

        # Check status of KSC services
        services = ["kladminserver", "kliam_srv", "ksc-web-console", "postgresql"]
        for s in services:
            stdin, stdout, stderr = client.exec_command(f"systemctl status {s}")
            out = stdout.read().decode("utf-8", errors="replace")
            print(f"=== Status {s} ===")
            print(out.encode("ascii", errors="replace").decode("ascii"))
            print("-" * 50)

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
