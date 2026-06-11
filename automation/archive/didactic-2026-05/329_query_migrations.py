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

        # Find migration tables
        q1 = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%migration%' ORDER BY table_schema, table_name;"
        cmd1 = f'sudo -S -u postgres psql -d ksciam -c "{q1}"'

        stdin, stdout, stderr = client.exec_command(cmd1)
        stdin.write(password + "\n")
        stdin.flush()

        tables_out = stdout.read().decode("utf-8", errors="replace")
        print("--- Migration Tables Found ---")
        print(tables_out)

        # Let's also query public.schema_migrations if it exists, and iam.schema_migrations, etc.
        # Let's list schemas and find if any other schemas have schema_migrations
        for schema in [
            "public",
            "iam",
            "voltron",
            "client",
            "ksc",
            "locker",
            "pat",
            "scope",
        ]:
            print(f"--- Content of {schema}.schema_migrations (if exists) ---")
            q2 = f"SELECT * FROM {schema}.schema_migrations;"
            cmd2 = f'sudo -S -u postgres psql -d ksciam -c "{q2}"'
            stdin, stdout, stderr = client.exec_command(cmd2)
            stdin.write(password + "\n")
            stdin.flush()
            print(stdout.read().decode("utf-8", errors="replace"))
            err = stderr.read().decode("utf-8", errors="replace")
            if err.strip():
                print(f"Error for {schema}: {err.strip()}")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
