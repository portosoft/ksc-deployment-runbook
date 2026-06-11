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

        # Show columns of spl_users
        q_cols = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'spl_users';"
        cmd = f'sudo -S -u postgres psql -d ksc -c "{q_cols}"'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print("--- Columns of spl_users ---")
        print(stdout.read().decode("utf-8"))

        # Query kscadmin and kscadmin2 in spl_users
        q_rows = (
            "SELECT * FROM spl_users WHERE \"wstrName\" IN ('kscadmin', 'kscadmin2');"
        )
        cmd2 = f'sudo -S -u postgres psql -d ksc -c "\\x" -c "{q_rows}"'
        stdin, stdout, stderr = client.exec_command(cmd2)
        stdin.write(password + "\n")
        stdin.flush()
        print("--- Rows in spl_users ---")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
