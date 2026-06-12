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
            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()
            return out, err

        def run_query(q):
            cmd = f'sudo -u postgres psql -d ksciam -t -A -c "{q}"'
            out, err = run_cmd(cmd)
            return out

        # Monitor loop
        for i in range(1, 11):
            print(f"\n--- Checking Progress (Iteration {i}/10) ---")

            # Check version
            q_ver = "SELECT version, dirty FROM public.schema_migrations LIMIT 1;"
            ver_out = run_query(q_ver)
            print("Migration State (version|dirty):", ver_out)

            # Check tables count in 'iam' schema
            q_cnt = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'iam' AND table_type = 'BASE TABLE';"
            cnt_out = run_query(q_cnt)
            print("Tables count in schema 'iam':", cnt_out)

            # Check status of service
            status_out, _ = run_cmd("systemctl is-active kliam_srv")
            print("kliam_srv status:", status_out)

            # Check logs
            print("Recent service logs (last 5 lines):")
            log_out, _ = run_cmd("sudo journalctl -u kliam_srv -n 5 --no-pager")
            # clean sudo prompt if any
            clean_log = "\n".join([line for line in log_out.split("\n") if "senha" not in line and "password" not in line])
            print(clean_log)

            time.sleep(5)

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
