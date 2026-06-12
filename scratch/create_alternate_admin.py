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

        # Create alternate admin user
        alt_name = "kscadmin2"
        alt_pass = "r8hk@bCo^53bNbDt"

        print(f"Creating alternate admin user '{alt_name}'...")
        cmd_add = f'sudo -S /opt/kaspersky/ksc64/sbin/kladduser -n "{alt_name}" -p "{alt_pass}"'
        stdin, stdout, stderr = client.exec_command(cmd_add)
        stdin.write(password + "\n")
        stdin.flush()

        out_add = stdout.read().decode("utf-8").strip()
        err_add = stderr.read().decode("utf-8").strip()
        print("--- kladduser STDOUT ---")
        print(out_add)
        print("--- kladduser STDERR ---")
        print(err_add)

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
