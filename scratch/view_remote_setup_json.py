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
            "sudo -S cat /etc/ksc-web-console-setup.json",
            "sudo -S ls -la /etc/ksc-web-console-setup.json",
            "sudo -S systemctl daemon-reload",
            "sudo -S systemctl restart ksc-web-console",
            "sudo -S systemctl status ksc-web-console --no-pager"
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
