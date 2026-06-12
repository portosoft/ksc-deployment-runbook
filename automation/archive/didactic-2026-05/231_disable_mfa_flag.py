import paramiko
import os
import time
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

        # Set the MFA flag to false
        cmd_set = "sudo -S LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klscflag -ssvset -pv klserver -s 87 -n KLSRV_SP_MFA_ENABLED -sv false -svt BOOL_T -ss '|ss_type = \"SS_SETTINGS\";'"
        stdin, stdout, stderr = client.exec_command(cmd_set)
        stdin.write(password + "\n")
        stdin.flush()
        print("Set stdout:", stdout.read().decode("utf-8"))
        print("Set stderr:", stderr.read().decode("utf-8"))

        # Restart kladminserver_srv
        print("Restarting kladminserver_srv...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart kladminserver_srv"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read()
        stderr.read()

        # Restart kliam_srv
        print("Restarting kliam_srv...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart kliam_srv"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read()
        stderr.read()

        # Restart ksc-web-console
        print("Restarting ksc-web-console...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart ksc-web-console"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read()
        stderr.read()

        print("Waiting 15s for services to initialize...")
        time.sleep(15)

        # Verify the flag is set
        cmd_get = "sudo -S LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klscflag -ssvget -pv klserver -s 87 -n KLSRV_SP_MFA_ENABLED -ss '|ss_type = \"SS_SETTINGS\";'"
        stdin, stdout, stderr = client.exec_command(cmd_get)
        stdin.write(password + "\n")
        stdin.flush()
        print("Get stdout:", stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
