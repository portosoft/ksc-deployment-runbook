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
        print("--- Connected successfully to remote server ---")

        # Let's read lines around 241 of /var/opt/kaspersky/ksc-web-console/server/core/server.js
        cmd = "sudo -S sed -n '220,260p' /var/opt/kaspersky/ksc-web-console/server/core/server.js"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print("STDOUT:")
        print(stdout.read().decode("utf-8", errors="replace").strip())
        print("STDERR:")
        print(stderr.read().decode("utf-8", errors="replace").strip())

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
