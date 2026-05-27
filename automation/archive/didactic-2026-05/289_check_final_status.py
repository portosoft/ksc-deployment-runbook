import paramiko
import os
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        def run_cmd(cmd):
            use_sudo = "sudo" in cmd
            run_cmd = cmd.replace("sudo", "sudo -S", 1) if use_sudo else cmd
            stdin, stdout, stderr = client.exec_command(run_cmd)
            if use_sudo:
                stdin.write(password + "\n")
                stdin.flush()
            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()
            return out, err

        def run_query(q):
            cmd = f'sudo -u postgres psql -d ksciam -c "{q}"'
            out, err = run_cmd(cmd)
            return out

        def safe_print(text):
            print(text.encode("ascii", errors="replace").decode("ascii"))

        print("=== 1. public.schema_migrations ===")
        safe_print(run_query("SELECT * FROM public.schema_migrations;"))

        print("\n=== 2. Table Counts by Schema ===")
        q_cnts = """
        SELECT table_schema, COUNT(*), string_agg(table_name, ', ' order by table_name) as tables
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        GROUP BY table_schema
        ORDER BY table_schema;
        """
        safe_print(run_query(q_cnts))

        print("\n=== 3. service status (kliam_srv) ===")
        status_out, _ = run_cmd("systemctl status kliam_srv --no-pager -l")
        safe_print(status_out)

        print("\n=== 4. service logs (kliam_srv) ===")
        log_out, _ = run_cmd("sudo journalctl -u kliam_srv -n 30 --no-pager")
        clean_log = "\n".join([line for line in log_out.split("\n") if "senha" not in line and "password" not in line])
        safe_print(clean_log)

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
