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

        services = ["kladminserver_srv", "kliam_srv", "ksc-web-console"]
        for svc in services:
            print(f"Restarting {svc}...")
            stdin, stdout, stderr = client.exec_command(f"sudo -S systemctl restart {svc}")
            stdin.write(password + "\n")
            stdin.flush()
            out = stdout.read().decode("utf-8")
            err = stderr.read().decode("utf-8")
            print(f"stdout: {out}")
            print(f"stderr: {err}")

        for svc in services:
            print(f"--- Status for {svc} ---")
            stdin, stdout, stderr = client.exec_command(f"sudo -S systemctl status {svc}")
            stdin.write(password + "\n")
            stdin.flush()
            out = stdout.read().decode("utf-8", errors="replace")
            print(out.encode("ascii", errors="replace").decode("ascii"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
