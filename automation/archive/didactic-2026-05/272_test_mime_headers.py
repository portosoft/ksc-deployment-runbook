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

        # Test curl with different headers
        headers_tests = [
            "",
            "-H 'Accept-Encoding: gzip, deflate, br'",
            "-H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)'",
            "-H 'Accept-Encoding: gzip, deflate, br' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)'",
        ]

        for h in headers_tests:
            print(f"--- Testing with: {h} ---")
            cmd = f"curl -k -I {h} https://localhost:8080/js/ksc-wc-forms.js"
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
