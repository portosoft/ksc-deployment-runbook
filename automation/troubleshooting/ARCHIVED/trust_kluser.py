import paramiko
import os
import sys


def trust_kluser(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        hba_file = "/var/lib/pgsql/data/pg_hba.conf"
        print(f"--- Setting kluser to trust in {hba_file} ---")

        # We'll add a line at the top to allow kluser to connect without password from 127.0.0.1
        line = "host    ksciam          kluser          127.0.0.1/32            trust\n"

        # Read file
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {hba_file}")
        stdin.write(password + "\n")
        stdin.flush()
        content = stdout.read().decode("utf-8")

        if "kluser" in content and "trust" in content:
            print("kluser already set to trust (or mentioned). Checking details...")

        # Prepend the line
        new_content = line + content

        sftp = client.open_sftp()
        with sftp.file("/tmp/pg_hba.conf", "w") as f:
            f.write(new_content)
        sftp.close()

        # Move back and reload pg
        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/pg_hba.conf {hba_file}'
        )
        client.exec_command(f'echo "{password}" | sudo -S systemctl reload postgresql')

        print("PostgreSQL reloaded with trust for kluser.")

        # Now restart IAM and Console
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart kliam_srv.service'
        )
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    trust_kluser(host, user, password)
