import paramiko
import os
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    ksc_db = os.getenv("KSC_DB_NAME")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Search for 'kscadmin' in all tables of ksc
        print(f"Searching in {ksc_db} database...")
        # Get all tables in public schema
        q_tables = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = 'public';"
        cmd = f'sudo -S -u postgres psql -d "{ksc_db}" -t -A -c "{q_tables}"'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        tables = stdout.read().decode("utf-8").strip().split("\n")

        for table in tables:
            if not table or "|" not in table:
                continue
            schema, name = table.split("|")
            # Get columns
            q_cols = f"SELECT column_name FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='{name}';"
            cmd_cols = f'sudo -S -u postgres psql -d "{ksc_db}" -t -A -c "{q_cols}"'
            stdin, stdout, stderr = client.exec_command(cmd_cols)
            stdin.write(password + "\n")
            stdin.flush()
            cols = stdout.read().decode("utf-8").strip().split("\n")

            searchable = [c for c in cols if any(x in c.lower() for x in ['name', 'login', 'user', 'email', 'id'])]
            if searchable:
                or_conds = " OR ".join([f"CAST({c} AS TEXT) ILIKE '%kscadmin%'" for c in searchable])
                q_search = f"SELECT * FROM {schema}.{name} WHERE {or_conds};"
                cmd_search = f'sudo -S -u postgres psql -d "{ksc_db}" -c "{q_search}"'
                stdin, stdout, stderr = client.exec_command(cmd_search)
                stdin.write(password + "\n")
                stdin.flush()
                res = stdout.read().decode("utf-8").strip()
                if res and "0 rows" not in res:
                    print(f"[{ksc_db}] Match in {schema}.{name}:")
                    print(res)

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
