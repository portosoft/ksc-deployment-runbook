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

        sql_script = """
-- Let's query binId for our users
SELECT "wstrName", "binId" FROM spl_users WHERE "wstrName" IN ('kscadmin', 'kscadmin2');

-- Clean existing exceptions
TRUNCATE mfa_totp_exceptions;

-- Insert exception for kscadmin
INSERT INTO mfa_totp_exceptions ("binId", "wstrName")
SELECT "binId", "wstrName" FROM spl_users WHERE "wstrName" = 'kscadmin';

-- Insert exception for kscadmin2
INSERT INTO mfa_totp_exceptions ("binId", "wstrName")
SELECT "binId", "wstrName" FROM spl_users WHERE "wstrName" = 'kscadmin2';

-- Query results to verify
SELECT * FROM mfa_totp_exceptions;
SELECT "wstrSamAccountName", "bTotpAllowed", "bTotpException", "bTotpReigstered"
FROM v_ak_users_and_groups_with_mfa
WHERE "wstrSamAccountName" IN ('kscadmin', 'kscadmin2');
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/insert_exceptions.sql", "w")
        f.write(sql_script)
        f.close()
        sftp.close()

        # Run SQL script
        print("Inserting exceptions in DB...")
        cmd = "sudo -S -u postgres psql -d ksc -f /tmp/insert_exceptions.sql"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/insert_exceptions.sql")

        # Restart KSC services
        services = ["kladminserver_srv", "kliam_srv", "ksc-web-console"]
        for svc in services:
            print(f"Restarting {svc}...")
            stdin, stdout, stderr = client.exec_command(f"sudo -S systemctl restart {svc}")
            stdin.write(password + "\n")
            stdin.flush()
            stdout.read(); stderr.read()

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
