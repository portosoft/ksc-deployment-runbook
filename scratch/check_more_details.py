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
            cmd = f'sudo -S -u postgres psql -d ksciam -c "{q}"'
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            out = stdout.read().decode("utf-8", errors="replace").strip()
            return out

        print("=== Indexes on iam.resources_schedule ===")
        q_idx = "SELECT indexname, indexdef FROM pg_indexes WHERE schemaname='iam' AND tablename='resources_schedule';"
        print(run_query(q_idx))

        print("\n=== Details of sessions_pkey constraint ===")
        q_pkey = """
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = 'ksc.sessions'::regclass AND i.indisprimary;
        """
        print(run_query(q_pkey))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
