import paramiko
import os
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    db_name = os.getenv("KSC_IAM_NAME")
    admin_name = os.getenv("KSC_ADMIN_NAME")
    admin_pass = os.getenv("KSC_ADMIN_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Run kladduser with correct flags: -n and -p
        print(f"Running kladduser for '{admin_name}' using correct flags...")
        cmd_add = f'sudo -S /opt/kaspersky/ksc64/sbin/kladduser -n "{admin_name}" -p "{admin_pass}"'
        stdin, stdout, stderr = client.exec_command(cmd_add)
        stdin.write(password + "\n")
        stdin.flush()

        out_add = stdout.read().decode("utf-8").strip()
        err_add = stderr.read().decode("utf-8").strip()
        print("--- kladduser STDOUT ---")
        print(out_add)
        print("--- kladduser STDERR ---")
        print(err_add)

        # Query the database to see if kscadmin exists now
        q = f"SELECT name, id FROM iam.users WHERE name = '{admin_name}';"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode("utf-8").strip()
        print("--- IAM Database Query ---")
        print(results if results else "Still not found!")

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
