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

        def run_query(q):
            cmd = f'sudo -S -u postgres psql -d ksc -c "{q}"'
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()
            return out, err

        print("=== Schemas and table counts in database 'ksc' ===")
        q = """
        SELECT table_schema, COUNT(*), string_agg(table_name, ', ' order by table_name) as tables
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        GROUP BY table_schema
        ORDER BY table_schema;
        """
        out, err = run_query(q)
        print(out)

        print("=== Views in database 'ksc' ===")
        q_view = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'VIEW'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name;
        """
        out_v, err_v = run_query(q_view)
        print(out_v)

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
