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
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Restart kliam_srv
        print("Restarting kliam_srv...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart kliam_srv"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print("Restart stdout:", stdout.read().decode("utf-8"))
        print("Restart stderr:", stderr.read().decode("utf-8"))

        print("Waiting 10 seconds for sync...")
        time.sleep(10)

        # Check status and logs of kliam_srv
        stdin, stdout, stderr = client.exec_command("systemctl status kliam_srv")
        print("--- status kliam_srv ---")
        out = stdout.read().decode("utf-8", errors="replace")
        print(out.encode("ascii", errors="replace").decode("ascii"))

        # Query all users from iam.users
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
