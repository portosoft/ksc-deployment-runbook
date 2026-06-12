import paramiko
import os
import sys
import time
from dotenv import load_dotenv

def safe_print(label, content_bytes):
    sys.stdout.buffer.write(f"\n--- {label} ---\n".encode("utf-8"))
    decoded = content_bytes.decode("utf-8", errors="replace").replace("\u25cf", "*").replace("\ufeff", "")
    encoded = decoded.encode(sys.stdout.encoding or "utf-8", errors="replace")
    sys.stdout.buffer.write(encoded + b"\n")

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

        # Read setup.json
        stdin, stdout, stderr = client.exec_command("sudo -S cat /etc/ksc-web-console-setup.json")
        stdin.write(password + "\n")
        stdin.flush()
        out_bytes = stdout.read()
        err_bytes = stderr.read()
        safe_print("/etc/ksc-web-console-setup.json STDOUT", out_bytes)
        safe_print("/etc/ksc-web-console-setup.json STDERR", err_bytes)

        # Run setup.js in exec_command
        print("Running setup.js...")
        stdin, stdout, stderr = client.exec_command("cd /var/opt/kaspersky/ksc-web-console && sudo -S /var/opt/kaspersky/ksc-web-console/node setup.js /etc/ksc-web-console-setup.json")
        stdin.write(password + "\n")
        stdin.flush()

        # Read stdout/stderr
        time.sleep(3)
        out_bytes = stdout.read()
        err_bytes = stderr.read()
        safe_print("setup.js STDOUT", out_bytes)
        safe_print("setup.js STDERR", err_bytes)

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
