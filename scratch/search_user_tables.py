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

        q = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
          AND (table_name ILIKE '%user%' OR table_name ILIKE '%role%' OR table_name ILIKE '%member%' OR table_name ILIKE '%group%' OR table_name ILIKE '%settings%')
        ORDER BY table_name;
        """
        cmd = f'sudo -S -u postgres psql -d ksc -c "{q}"'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print("--- Matching tables ---")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
