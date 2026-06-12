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

        # Grep search using strings on binaries in /opt/kaspersky/ksc64/lib/ and /opt/kaspersky/ksc64/sbin/
        cmd = "find /opt/kaspersky/ksc64/ -type f | xargs -n 50 strings 2>/dev/null | grep -i 'forbidden' | head -n 40"
        stdin, stdout, stderr = client.exec_command(cmd)
        print("--- Strings 'forbidden' ---")
        print(stdout.read().decode("utf-8", errors="replace"))

        cmd2 = "find /opt/kaspersky/ksc64/ -type f | xargs -n 50 strings 2>/dev/null | grep -i 'factor' | head -n 40"
        stdin, stdout, stderr = client.exec_command(cmd2)
        print("--- Strings 'factor' ---")
        print(stdout.read().decode("utf-8", errors="replace"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
