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
            err = stderr.read().decode("utf-8", errors="replace").strip()
            return out, err

        print("=== 1. Inspecting ksc.challenges ===")
        out, err = run_query(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='ksc' AND table_name='challenges';"
        )
        print("Columns:")
        print(out)
        out, err = run_query("SELECT COUNT(*) FROM ksc.challenges;")
        print("Row count:", out)

        print("\n=== 2. Inspecting iam.resources_schedule ===")
        out, err = run_query(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='iam' AND table_name='resources_schedule';"
        )
        print("Columns:")
        print(out)
        out, err = run_query(
            "SELECT conname, contype FROM pg_constraint WHERE conrelid = 'iam.resources_schedule'::regclass;"
        )
        print("Constraints:")
        print(out)
        out, err = run_query("SELECT COUNT(*) FROM iam.resources_schedule;")
        print("Row count:", out)

        print("\n=== 3. Inspecting index ksc_directory_object_uniq_idx ===")
        out, err = run_query(
            "SELECT indexname FROM pg_indexes WHERE schemaname='ksc' AND tablename='directory_object';"
        )
        print("Indexes:")
        print(out)

        print("\n=== 4. Inspecting ksc.sessions ===")
        out, err = run_query(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='ksc' AND table_name='sessions';"
        )
        print("Columns:")
        print(out)
        out, err = run_query(
            "SELECT conname, contype FROM pg_constraint WHERE conrelid = 'ksc.sessions'::regclass;"
        )
        print("Constraints:")
        print(out)
        out, err = run_query("SELECT COUNT(*) FROM ksc.sessions;")
        print("Row count:", out)

        print("\n=== 5. Inspecting ksc.deleting_outbox ===")
        out, err = run_query(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='ksc' AND table_name='deleting_outbox');"
        )
        print("Exists:", out)
        out, err = run_query("SELECT COUNT(*) FROM ksc.deleting_outbox;")
        print("Row count (if exists):", out)

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
