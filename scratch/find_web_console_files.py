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
        print("--- Connected successfully to remote server ---")

        cmds = [
            "rpm -qa | grep ksc",
            "find /var/opt/kaspersky/ -maxdepth 3",
            "find /opt/kaspersky/ -maxdepth 3",
            "which node",
            "systemctl cat ksc-web-console"
        ]

        for cmd in cmds:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            out_bytes = stdout.read()
            err_bytes = stderr.read()
            print("STDOUT:")
            print(out_bytes.decode("utf-8", errors="replace").strip())
            print("STDERR:")
            print(err_bytes.decode("utf-8", errors="replace").strip())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
