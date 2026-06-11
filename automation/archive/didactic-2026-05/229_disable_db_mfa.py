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

        # SQL script to disable MFA in database
        sql = """
        -- Set required to false
        UPDATE mfa_totp_settings SET bMfaRequiredForAll = 0 WHERE nIdentity = 1;
        -- Clear allowed list
        TRUNCATE mfa_totp_allowed;
        -- Clear secrets and exceptions just in case
        TRUNCATE mfa_totp_secrets;
        TRUNCATE mfa_totp_exceptions;
        """

        cmd = f'sudo -S -u postgres psql -d ksc -c "{sql}"'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print("--- SQL Output ---")
        print(stdout.read().decode("utf-8"))
        print(stderr.read().decode("utf-8"))

        # Restart KSC services
        print("Restarting kladminserver_srv...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart kladminserver_srv"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read()
        stderr.read()

        print("Restarting kliam_srv...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart kliam_srv"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read()
        stderr.read()

        print("Restarting ksc-web-console...")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart ksc-web-console"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.read()
        stderr.read()

        print("Waiting 15s for services to stabilize...")
        time.sleep(15)

        print("Verification query:")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S -u postgres psql -d ksc -c 'SELECT * FROM mfa_totp_settings; SELECT * FROM mfa_totp_allowed;'"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
