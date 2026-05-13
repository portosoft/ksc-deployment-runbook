import paramiko
import os
import sys

def update_db_pass(host, user, password, db_pass):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password)

    # Using a temp SQL file to avoid shell expansion issues with special chars
    client.exec_command(f"echo \"SET password_encryption = 'md5'; ALTER USER kluser WITH PASSWORD '{db_pass}';\" > /tmp/update.sql")
    stdin, stdout, stderr = client.exec_command("sudo -S sudo -u postgres psql -f /tmp/update.sql")
    stdin.write(password + '\n')
    stdin.flush()
    print(stdout.read().decode())
    client.exec_command("rm -f /tmp/update.sql")
    client.close()

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    db_pass = os.getenv("KSC_DB_PASS")

    update_db_pass(host, user, password, db_pass)
