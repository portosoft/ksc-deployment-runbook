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

        # Let's search inside setup.js for file paths or JSON loading
        cmd = "sudo -S grep -n -E 'JSON.parse|fs.readFileSync|require' /var/opt/kaspersky/ksc-web-console/setup.js"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print("STDOUT:")
        # Print with cp1252/sys.stdout.encoding safety
        out_str = stdout.read().decode("utf-8", errors="replace")
        sys.stdout.buffer.write(
            out_str.encode(sys.stdout.encoding or "utf-8", errors="replace") + b"\n"
        )

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
