import paramiko
import os
import time
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
            out = stdout.read().decode("utf-8", errors="replace")
            err = stderr.read().decode("utf-8", errors="replace")
            return out, err

        print("Stopping kliam_srv...")
        run_cmd("sudo systemctl stop kliam_srv")
        time.sleep(2)

        print("Clearing schema_migrations...")
        run_cmd(
            'sudo -u postgres psql -d ksciam -c "DELETE FROM public.schema_migrations;"'
        )

        # Get current time for journalctl since
        print("Starting kliam_srv and capturing logs...")
        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        run_cmd("sudo systemctl start kliam_srv")

        # Let's wait 10 seconds for the migration to run and fail
        time.sleep(10)

        # Retrieve logs since start_time
        print("Retrieving logs...")
        cmd_logs = f'sudo journalctl -u kliam_srv --since "{start_time}" --no-pager'
        out, err = run_cmd(cmd_logs)

        print("=== kliam_srv Migration Logs ===")
        print(out)
        if err.strip():
            print("=== stderr ===")
            print(err)

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
