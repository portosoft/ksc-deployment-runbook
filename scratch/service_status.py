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

        stdin, stdout, stderr = client.exec_command("sudo -S systemctl status ksc-web-console")
        stdin.write(password + "\n")
        stdin.flush()
        out = stdout.read().decode("utf-8", errors="replace")
        print(out.encode("ascii", errors="replace").decode("ascii"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
