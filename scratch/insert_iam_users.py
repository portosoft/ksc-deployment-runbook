import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password)

    print("=== Inserting kscadmin2 into iam.accounts ===")

    query = """
    INSERT INTO iam.accounts (id, email, full_name, user_login, is_service, idp_access_allowed)
    VALUES
    (gen_random_uuid(), 'kscadmin2@localhost', 'Administrator 2', 'kscadmin2', false, false),
    (gen_random_uuid(), 'kladmins@localhost', 'KLAdmins', 'KLAdmins', false, false);
    """
    cmd = f'sudo -S -u postgres psql -d ksciam -c "{query}"'
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))

    client.close()

if __name__ == "__main__":
    main()
