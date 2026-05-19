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

        # Check ksc-web-console service status
        stdin, stdout, stderr = client.exec_command("systemctl status ksc-web-console")
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        print("--- ksc-web-console service status ---")
        # Replace non-ascii chars to avoid console print errors on Windows
        print(out.encode("ascii", errors="replace").decode("ascii"))
        if err:
            print(
                "Error checking service:",
                err.encode("ascii", errors="replace").decode("ascii"),
            )

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
