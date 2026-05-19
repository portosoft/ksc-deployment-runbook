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

        # Restart service
        print("Restarting ksc-web-console...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart ksc-web-console"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print("Restart stdout:", stdout.read().decode("utf-8"))
        print("Restart stderr:", stderr.read().decode("utf-8"))

        # Wait a moment
        import time

        time.sleep(3)

        # Check status
        stdin, stdout, stderr = client.exec_command("systemctl status ksc-web-console")
        print("--- status ---")
        print(
            stdout.read()
            .decode("utf-8", errors="replace")
            .encode("ascii", errors="replace")
            .decode("ascii")
        )

        # Check journal logs
        print("--- journal logs (last 30 lines) ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S journalctl -u ksc-web-console -n 30 --no-pager"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(
            stdout.read()
            .decode("utf-8", errors="replace")
            .encode("ascii", errors="replace")
            .decode("ascii")
        )

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
