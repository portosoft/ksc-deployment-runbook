import paramiko
import os
import sys
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
        print("--- Connected successfully to remote server ---")

        cmds = ["sudo -S head -n 100 /var/opt/kaspersky/ksc-web-console/index.js"]

        for cmd in cmds:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            out_bytes = stdout.read()

            out_str = out_bytes.decode("utf-8", errors="replace").replace("\u25cf", "*")
            sys.stdout.buffer.write(
                out_str.encode(sys.stdout.encoding or "utf-8", errors="replace") + b"\n"
            )

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
