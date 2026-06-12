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

        # Query the MFA flag
        cmd = "sudo -S LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klscflag -ssvget -pv klserver -s 87 -n KLSRV_SP_MFA_ENABLED -ss '|ss_type = \"SS_SETTINGS\";'"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print("--- klscflag stdout ---")
        print(stdout.read().decode("utf-8"))
        print("--- klscflag stderr ---")
        print(stderr.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
