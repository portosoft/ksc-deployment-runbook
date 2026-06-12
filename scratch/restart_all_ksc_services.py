import paramiko
import os
import time
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    db_name = os.getenv("KSC_IAM_NAME")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Restart kladminserver_srv
        print("Restarting kladminserver_srv...")
        stdin, stdout, stderr = client.exec_command("sudo -S systemctl restart kladminserver_srv")
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read(); stderr.read()

        print("Waiting 30 seconds before restarting kliam_srv...")
        time.sleep(30)

        # Restart kliam_srv
        print("Restarting kliam_srv...")
        stdin, stdout, stderr = client.exec_command("sudo -S systemctl restart kliam_srv")
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read(); stderr.read()

        print("Waiting 30 seconds before restarting ksc-web-console...")
        time.sleep(30)

        # Restart ksc-web-console
        print("Restarting ksc-web-console...")
        stdin, stdout, stderr = client.exec_command("sudo -S systemctl restart ksc-web-console")
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read(); stderr.read()

        print("Waiting 30 seconds for services to fully initialize...")
        time.sleep(30)

        # Verify status of all services
        for svc in ["kladminserver_srv", "kliam_srv", "ksc-web-console"]:
            print(f"Checking status of {svc}...")
            _, stdout_s, _ = client.exec_command(f"systemctl is-active {svc}")
            print(f"Status of {svc}: {stdout_s.read().decode('utf-8').strip()}")

        # Check user database
        q = "SELECT name, id FROM iam.users;"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -c "{q}"'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print("--- iam.users ---")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
