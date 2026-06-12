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
            "sudo -S ss -tulpn | grep -E '13299|8080|13000|14000|9500'",
            "sudo -S systemctl status kladminserver_srv.service | grep Active",
            "sudo -S systemctl status kliam_srv.service | grep Active",
            "sudo -S systemctl status ksc-web-console.service | grep Active",
            "LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klscflag -ssvget -pv klserver -s 87 -n KLSRV_SP_OPEN_OAPI_PORT -ss '|ss_type = \"SS_SETTINGS\";'"
        ]

        for cmd in cmds:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            print("STDOUT:")
            print(stdout.read().decode("utf-8").strip())
            print("STDERR:")
            print(stderr.read().decode("utf-8").strip())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
