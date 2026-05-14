import sys
import os
import paramiko

# Add lib to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, commands, upload_file=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)

    if upload_file:
        sftp = client.open_sftp()
        with open(upload_file['local'], 'w') as f:
            f.write(upload_file['content'])
        sftp.put(upload_file['local'], upload_file['remote'])
        sftp.close()
        os.remove(upload_file['local'])

    for cmd in commands:
        print(f"Executing: {cmd}")
        # Use a more robust way to execute commands
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        stdin.write(password + '\n')
        stdin.flush()
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out: print(f"Output: {out}")
        if err and "sudo: a senha" not in err: print(f"Error: {err}")
    client.close()

secrets = vault.decrypt_secrets()

# Step 1: Prepare Postgres
# Use single quotes for the SQL password and escape shell chars
pg_cmds = [
    f"sudo -u postgres psql -c \"CREATE USER kluser WITH PASSWORD 'REDACTED_DB_PASS' SUPERUSER;\" || true",
    "sudo -u postgres psql -c \"CREATE DATABASE ksc OWNER kluser;\" || true",
    "sudo -u postgres psql -c \"CREATE DATABASE ksciam OWNER kluser;\" || true"
]

# Step 2: Postinstall
ans_content = f"""EULA_ACCEPTED=1
PP_ACCEPTED=1
KLSRV_UNATT_DBMS_TYPE=Postgres
KLSRV_UNATT_DBMS_INSTANCE=127.0.0.1
KLSRV_UNATT_DBMS_PORT=5432
KLSRV_UNATT_DBMS_LOGIN=kluser
KLSRV_UNATT_DBMS_PASSWORD={secrets['DB_PASS']}
KLSRV_UNATT_DB_NAME=ksc
KLSRV_UNATT_DBMS_IAM_TYPE=Postgres
KLSRV_UNATT_DBMS_IAM_INSTANCE=127.0.0.1
KLSRV_UNATT_DBMS_IAM_PORT=5432
KLSRV_UNATT_DBMS_IAM_LOGIN=kluser
KLSRV_UNATT_DBMS_IAM_PASSWORD={secrets['DB_PASS']}
KLSRV_UNATT_DB_IAM_NAME=ksciam
KLSRV_UNATT_SERVERADDRESS={secrets['KSC_FQDN']}
KLSRV_UNATT_IAM_ADDRESS={secrets['KSC_FQDN']}
KLSRV_UNATT_KLSVCUSER=ksc
KLSRV_UNATT_KLADMINSGROUP=kladmins
KLSRV_UNATT_KLIAMUSER=ksc
KLSRV_UNATT_KLSRVUSER=ksc
"""

ksc_cmds = [
    "LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib KLAUTOANSWERS=/tmp/ksc_answers.txt /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl",
    "rm -f /tmp/ksc_answers.txt"
]

print("--- Preparing PostgreSQL ---")
run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], pg_cmds)

print("--- Running KSC Postinstall ---")
run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], ksc_cmds,
        upload_file={'local': 'ksc_ans.tmp', 'remote': '/tmp/ksc_answers.txt', 'content': ans_content})
