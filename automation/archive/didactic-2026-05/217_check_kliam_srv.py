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

        # Check kliam_srv status
        stdin, stdout, stderr = client.exec_command("systemctl status kliam_srv")
        print("--- status kliam_srv ---")
        print(
            stdout.read()
            .decode("utf-8", errors="replace")
            .encode("ascii", errors="replace")
            .decode("ascii")
        )

        # Check journalctl logs
        print("--- journal logs (last 30 lines) ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S journalctl -u kliam_srv -n 30 --no-pager"
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
