import paramiko
import os
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Query all rows in spl_users
        q1 = "SELECT * FROM spl_users;"
        cmd1 = f'sudo -S -u postgres psql -d ksc -c "{q1}"'
        stdin, stdout, stderr = client.exec_command(cmd1)
        stdin.write(password + "\n")
        stdin.flush()
        print("--- spl_users rows ---")
        print(stdout.read().decode("utf-8"))

        # Query all rows in ak_users
        q2 = "SELECT * FROM ak_users;"
        cmd2 = f'sudo -S -u postgres psql -d ksc -c "{q2}"'
        stdin, stdout, stderr = client.exec_command(cmd2)
        stdin.write(password + "\n")
        stdin.flush()
        print("--- ak_users rows ---")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
