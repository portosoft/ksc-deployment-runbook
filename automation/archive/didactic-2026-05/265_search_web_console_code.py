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

        # Search for GenerateSecret using sudo grep in all files under /var/opt/kaspersky/ksc-web-console/
        cmd = "sudo -S grep -rn 'GenerateSecret' /var/opt/kaspersky/ksc-web-console/ 2>/dev/null | grep -v 'node_modules'"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print("--- Grep results ---")
        out = stdout.read().decode("utf-8", errors="replace")
        print(out.encode("ascii", errors="replace").decode("ascii"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
