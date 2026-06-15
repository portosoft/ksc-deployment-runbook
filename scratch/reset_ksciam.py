import os
import sys
import paramiko
from dotenv import load_dotenv

def reset_iam_db():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    if not all([host, user, password]):
        sys.exit(1)

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password)

    print("--- Stopping kliam_srv ---")
    client.exec_command(f"echo {password} | sudo -S systemctl stop kliam_srv")

    print("--- Resetting ksciam (Postgres) ---")
    db = "ksciam"
    cmd0 = f"echo {password} | sudo -S -u postgres psql -c \"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{db}' AND pid <> pg_backend_pid();\""
    client.exec_command(cmd0)

    cmd1 = f'echo {password} | sudo -S -u postgres psql -c "DROP DATABASE {db};"'
    stdin, stdout, stderr = client.exec_command(cmd1)
    print(f"Drop {db}: {stdout.read().decode().strip()}")

    cmd2 = f'echo {password} | sudo -S -u postgres psql -c "CREATE DATABASE {db} OWNER kluser;"'
    stdin, stdout, stderr = client.exec_command(cmd2)
    print(f"Create {db}: {stdout.read().decode().strip()}")

    print("--- Starting kliam_srv ---")
    client.exec_command(f"echo {password} | sudo -S systemctl start kliam_srv")

    print("--- Waiting 10 seconds for initialization ---")
    import time
    time.sleep(10)

    print("--- Restarting kladminserver_srv and ksc-web-console to force sync ---")
    client.exec_command(f"echo {password} | sudo -S systemctl restart kladminserver_srv ksc-web-console")

    client.close()

if __name__ == "__main__":
    reset_iam_db()
