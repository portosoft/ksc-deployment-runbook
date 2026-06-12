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
        print("Connected.")

        # 1. Locate the file on the server
        stdin, stdout, stderr = client.exec_command("find /var/opt/kaspersky/ksc-web-console/ -name 'ksc-wc-forms.js'")
        print("File path:", stdout.read().decode("utf-8").strip())

        # 2. Curl the URL on localhost to see the response headers
        cmd_curl = "curl -k -I https://localhost:8080/js/ksc-wc-forms.js"
        stdin, stdout, stderr = client.exec_command(cmd_curl)
        print("--- Curl Headers ---")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
