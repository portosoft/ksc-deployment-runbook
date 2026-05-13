import paramiko
import os
import sys

def sync_iam_password(host, user, password, new_iam_pass):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        iam_config = '/var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml'
        print(f"--- Updating {iam_config} with new password ---")

        # Use sed to replace the password line
        # Escape special characters in the new password for sed
        # SENHA_AQUI
        escaped_pass = new_iam_pass.replace('&', '\&').replace('#', '\#').replace('!', '\!')

        cmd = f'echo "{password}" | sudo -S sed -i "s/dbms_userpassword: .*/dbms_userpassword: \\"{new_iam_pass}\\"/" {iam_config}'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdout.read()

        print("--- Updating PostgreSQL kluser password ---")
        pg_cmd = f"sudo -u postgres psql -c \"ALTER USER kluser WITH PASSWORD '{new_iam_pass}';\""
        stdin, stdout, stderr = client.exec_command(pg_cmd)
        print(stdout.read().decode('utf-8'))

        # Restart kliam service if it exists, or restart web console which depends on it
        print("--- Restarting services ---")
        client.exec_command(f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service')

        client.close()
        print("Sync completed successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    new_iam_pass = "SENHA_AQUI"

    sync_iam_password(host, user, password, new_iam_pass)
