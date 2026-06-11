import paramiko
import os
import sys


def verify_and_restart_iam(host, user, password, iam_pass):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        print(f"--- Verifying password for kluser ---")
        # Use a more robust way to pass password to psql
        cmd = f"PGPASSWORD='{iam_pass}' psql -h 127.0.0.1 -U kluser -d ksciam -c 'SELECT 1;'"
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode("utf-8")
        err = stderr.read().decode("utf-8")
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")

        if "1 row" in out or "1" in out:
            print("Password verified successfully!")
        else:
            print("Password verification FAILED. Retrying ALTER USER...")
            pg_cmd = f"sudo -u postgres psql -c \"ALTER USER kluser WITH PASSWORD '{iam_pass}';\""
            stdin, stdout, stderr = client.exec_command(pg_cmd)
            stdout.read()

        print("--- Restarting kliam_srv.service ---")
        stdin, stdout, stderr = client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart kliam_srv.service'
        )
        stdout.read()

        print("--- Restarting ksc-web-console.service ---")
        stdin, stdout, stderr = client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )
        stdout.read()

        print("Services restarted.")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    iam_pass = "SENHA_AQUI"

    verify_and_restart_iam(host, user, password, iam_pass)
