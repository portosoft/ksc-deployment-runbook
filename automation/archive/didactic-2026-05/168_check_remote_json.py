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

        # Read /etc/ksc-web-console-setup.json
        stdin, stdout, stderr = client.exec_command(
            "cat /etc/ksc-web-console-setup.json"
        )
        out = stdout.read().decode("utf-8")
        err = stderr.read().decode("utf-8")
        print("--- /etc/ksc-web-console-setup.json ---")
        print(out)
        if err:
            print("Error reading file:", err)

        # Check ksc-web-console service status
        stdin, stdout, stderr = client.exec_command(
            "sudo systemctl status ksc-web-console"
        )
        stdin.write(password + "\n")
        stdin.flush()
        out = stdout.read().decode("utf-8")
        err = stderr.read().decode("utf-8")
        print("--- ksc-web-console service status ---")
        print(out)
        if err:
            print("Error checking service:", err)

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
