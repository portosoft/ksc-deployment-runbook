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

        cmds = [
            "rpm -qa | grep -E 'ksc|klnagent|web-console'",
            "sudo -S systemctl daemon-reload",
            "sudo -S systemctl restart ksc-web-console",
            "sudo -S systemctl status ksc-web-console --no-pager",
            "sudo -S ss -tulpn | grep 8080"
        ]

        for cmd in cmds:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            out_bytes = stdout.read()
            err_bytes = stderr.read()
            print("STDOUT:")
            # Decode with ignore to prevent encoding/decoding crashes
            print(out_bytes.decode("utf-8", errors="ignore").strip())
            print("STDERR:")
            print(err_bytes.decode("utf-8", errors="ignore").strip())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
