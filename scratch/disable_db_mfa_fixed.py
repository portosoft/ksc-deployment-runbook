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
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Let's write the SQL commands directly to a file on the server
        sql_content = """
UPDATE mfa_totp_settings SET "bMfaRequiredForAll" = 0 WHERE "nIdentity" = 1;
TRUNCATE mfa_totp_allowed;
TRUNCATE mfa_totp_secrets;
TRUNCATE mfa_totp_exceptions;
"""
        # Write to /tmp/disable_mfa.sql on the remote server
        sftp = client.open_sftp()
        f = sftp.file("/tmp/disable_mfa.sql", "w")
        f.write(sql_content)
        f.close()
        sftp.close()
        print("Uploaded SQL file to remote server.")

        # Execute the SQL file
        cmd = "sudo -S -u postgres psql -d ksc -f /tmp/disable_mfa.sql"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print("--- SQL Output ---")
        print(stdout.read().decode("utf-8"))
        print(stderr.read().decode("utf-8"))

        # Clean up SQL file
        client.exec_command("rm -f /tmp/disable_mfa.sql")

        # Restart KSC services
        print("Restarting kladminserver_srv...")
        stdin, stdout, stderr = client.exec_command("sudo -S systemctl restart kladminserver_srv")
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read(); stderr.read()

        print("Restarting kliam_srv...")
        stdin, stdout, stderr = client.exec_command("sudo -S systemctl restart kliam_srv")
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read(); stderr.read()

        print("Restarting ksc-web-console...")
        stdin, stdout, stderr = client.exec_command("sudo -S systemctl restart ksc-web-console")
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read(); stderr.read()

        print("Waiting 15s for services to stabilize...")
        time.sleep(15)

        print("Verification query:")
        stdin, stdout, stderr = client.exec_command("sudo -S -u postgres psql -d ksc -c 'SELECT * FROM mfa_totp_settings; SELECT * FROM mfa_totp_allowed;'")
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
