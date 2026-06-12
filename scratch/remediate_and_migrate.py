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
            cmd = f'sudo -u postgres psql -d ksciam -c "{q}"'
            out, err = run_cmd(cmd)
            return out

        # 1. Stop kliam_srv
        print("Stopping kliam_srv...")
        run_cmd("sudo systemctl stop kliam_srv")
        time.sleep(2)

        # 2. Run Database Remediation Queries
        print("Running database remediation queries...")
        queries = [
            # 1. Challenges remediation
            "ALTER TABLE ksc.challenges DROP COLUMN IF EXISTS ui_locales;",

            # 2. Resources schedule remediation
            "ALTER TABLE iam.resources_schedule DROP COLUMN IF EXISTS req_id;",
            "ALTER TABLE iam.resources_schedule DROP CONSTRAINT IF EXISTS resources_schedule_pkey;",
            "ALTER TABLE iam.resources_schedule ADD CONSTRAINT resources_schedule_pkey PRIMARY KEY (id);",
            "CREATE UNIQUE INDEX IF NOT EXISTS iam_schedule_uq ON iam.resources_schedule (id, policy_id);",
            "DROP INDEX IF EXISTS iam.obj_ops_unique;",

            # 3. Directory object index remediation
            "DROP INDEX IF EXISTS ksc.ksc_directory_object_uniq_idx;",
            # Revert tenant_id column type to scalar varchar(255) so the array conversion migration runs cleanly
            "ALTER TABLE ksc.directory_object ALTER COLUMN tenant_id TYPE varchar(255) USING tenant_id[1];",

            # 4. Sessions columns and constraints remediation
            "ALTER TABLE ksc.sessions DROP CONSTRAINT IF EXISTS sessions_pkey;",
            "ALTER TABLE ksc.sessions DROP COLUMN IF EXISTS workspace_id;",
            "ALTER TABLE ksc.sessions ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);",

            # 5. Outbox table remediation
            "DROP TABLE IF EXISTS ksc.deleting_outbox;",

            # 6. Reset migration version in public.schema_migrations to 1751873842
            "DELETE FROM public.schema_migrations;",
            "INSERT INTO public.schema_migrations (version, dirty) VALUES (1751873842, false);"
        ]

        for q in queries:
            print(f"Executing: {q}")
            res = run_query(q)
            print(res)
            print("-" * 50)

        # 3. Start kliam_srv
        print("Starting kliam_srv...")
        out, err = run_cmd("sudo systemctl start kliam_srv")
        print("STDOUT:", out)
        print("STDERR:", err)

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
