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

        # Try HTTP first
        print("Testing HTTP connection to port 8080...")
        stdin, stdout, stderr = client.exec_command("curl -k -I http://localhost:8080")
        print("--- curl http://localhost:8080 ---")
        print(stdout.read().decode("utf-8", errors="replace"))
        print(stderr.read().decode("utf-8", errors="replace"))

        # Try HTTPS
        print("Testing HTTPS connection to port 8080...")
        stdin, stdout, stderr = client.exec_command("curl -k -I https://localhost:8080")
        print("--- curl https://localhost:8080 ---")
        print(stdout.read().decode("utf-8", errors="replace"))
        print(stderr.read().decode("utf-8", errors="replace"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
