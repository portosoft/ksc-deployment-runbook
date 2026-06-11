import paramiko
import os
import sys


def ksc_pass_update(host, user, password, db_pass):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    client.connect(host, username=user, password=password)

    # Escape single quotes for the bash string
    safe_db_pass = db_pass.replace("'", "'\\''")

    # Ninja method: printf inside bash subshell under sudo
    cmd = f"sudo -S bash -c \"printf 'kluser\\n{safe_db_pass}\\n{safe_db_pass}\\n' | LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klsrvconfig -set_dbms_cred\""

    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()

    print(f"STDOUT: {stdout.read().decode()}")
    print(f"STDERR: {stderr.read().decode()}")
    client.close()


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    db_pass = os.getenv("KSC_DB_PASS")

    ksc_pass_update(host, user, password, db_pass)
