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

        q = """
        SELECT table_schema, COUNT(*), string_agg(table_name, ', ' order by table_name) as tables
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        GROUP BY table_schema
        ORDER BY table_schema;
        """
        cmd = f'sudo -S -u postgres psql -d ksc -c "{q}"'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print("--- Table Counts by Schema in ksc ---")
        print(stdout.read().decode("utf-8"))

        # Also search for "users" table or view in ksc database
        q_search = """
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_name ILIKE '%user%'
        ORDER BY table_schema, table_name;
        """
        cmd_search = f'sudo -S -u postgres psql -d ksc -c "{q_search}"'
        stdin, stdout, stderr = client.exec_command(cmd_search)
        stdin.write(password + "\n")
        stdin.flush()
        print("--- Tables/Views containing 'user' in ksc ---")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
