import paramiko
import os
import time
import re
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

        def run_cmd(cmd):
            use_sudo = "sudo" in cmd
            run_cmd = cmd.replace("sudo", "sudo -S", 1) if use_sudo else cmd
            stdin, stdout, stderr = client.exec_command(run_cmd)
            if use_sudo:
                stdin.write(password + "\n")
                stdin.flush()
            out = stdout.read().decode("utf-8", errors="replace")
            err = stderr.read().decode("utf-8", errors="replace")
            return out, err

        def get_migration_state():
            q = "SELECT version, dirty FROM public.schema_migrations LIMIT 1;"
            out, _ = run_cmd(f'sudo -u postgres psql -d ksciam -t -A -c "{q}"')
            out = out.strip()
            if not out:
                return None, None
            parts = out.split('|')
            if len(parts) == 2:
                version = int(parts[0])
                dirty = parts[1] == 't'
                return version, dirty
            return None, None

        def get_iam_table_count():
            q = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'iam' AND table_type = 'BASE TABLE';"
            out, _ = run_cmd(f'sudo -u postgres psql -d ksciam -t -A -c "{q}"')
            try:
                return int(out.strip())
            except:
                return 0

        # Loop to automatically resolve dirty migrations
        for step in range(1, 50):
            version, dirty = get_migration_state()
            print(f"\n--- STEP {step} ---")
            print(f"Current migration state: version={version}, dirty={dirty}")

            # Check table count in 'iam' schema
            tables_count = get_iam_table_count()
            print(f"Number of tables in schema 'iam': {tables_count}")

            # Check if service is active/running
            out_status, _ = run_cmd("systemctl is-active kliam_srv")
            status = out_status.strip()
            print(f"kliam_srv status: {status}")

            if not dirty:
                if status == "active":
                    print("Service is active and migration is clean! We have succeeded!")
                    break
                else:
                    print("Service is not active but migration is clean. Waiting 10s to see if it starts or fails...")
                    time.sleep(10)
                    out_status, _ = run_cmd("systemctl is-active kliam_srv")
                    status = out_status.strip()
                    if status == "active":
                        print("Service is now active!")
                        break

                    # Refresh state
                    version, dirty = get_migration_state()
                    if not dirty:
                        print("Still clean but inactive. Let's start the service.")
                        run_cmd("sudo systemctl start kliam_srv")
                        time.sleep(5)
                        continue

            # If dirty, we stop service, mark clean, and start
            print(f"Stopping kliam_srv to fix dirty version {version}...")
            run_cmd("sudo systemctl stop kliam_srv")
            time.sleep(1)

            print(f"Marking version {version} as clean...")
            q_update = f"UPDATE public.schema_migrations SET dirty = false WHERE version = {version};"
            run_cmd(f'sudo -u postgres psql -d ksciam -c "{q_update}"')

            print("Starting kliam_srv to run the next migration...")
            start_time = time.strftime("%Y-%m-%d %H:%M:%S")
            run_cmd("sudo systemctl start kliam_srv")

            # Wait for it to attempt next migration
            time.sleep(8)

            # Get logs for the attempt
            print("Migration attempt logs:")
            cmd_logs = f'sudo journalctl -u kliam_srv --since "{start_time}" --no-pager'
            out_logs, _ = run_cmd(cmd_logs)

            # Extract the error line
            err_lines = [line for line in out_logs.split('\n') if "error" in line.lower() or "fail" in line.lower()]
            for line in err_lines[:5]:
                print("  >", line.strip())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
