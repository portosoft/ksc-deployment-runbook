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

        # Show all from acl_role
        stdin, stdout, stderr = client.exec_command(
            "sudo -S -u postgres psql -d ksc -c 'SELECT * FROM acl_role;'"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print("--- acl_role ---")
        print(stdout.read().decode("utf-8"))

        # Show columns and first 20 records of acl_role_permission
        stdin, stdout, stderr = client.exec_command(
            "sudo -S -u postgres psql -d ksc -c 'SELECT * FROM acl_role_permission LIMIT 20;'"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print("--- acl_role_permission (first 20) ---")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
