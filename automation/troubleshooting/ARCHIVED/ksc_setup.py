import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv()


def run_ssh_commands_with_sudo(host, user, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        results = []
        for cmd in commands:
            full_cmd = f"sudo -S {cmd}"
            stdin, stdout, stderr = client.exec_command(full_cmd)
            stdin.write(password + "\n")
            stdin.flush()
            out = stdout.read().decode("utf-8")
            err = stderr.read().decode("utf-8")
            exit_status = stdout.channel.recv_exit_status()
            results.append(
                {
                    "command": cmd,
                    "stdout": out,
                    "stderr": err,
                    "exit_status": exit_status,
                }
            )
        client.close()
        return results
    except Exception as e:
        print(f"Erro: {e}")
        return None


def main():
    host = os.getenv("KSC_HOST", "SERVER_IP_REDACTED")
    user = os.getenv("KSC_USER", "suporte")
    password = os.getenv("KSC_PASS")
    db_pass = os.getenv("KSC_DB_PASS", "REDACTED_DB_PASS")
    fqdn = "kscserver.tail8b9ae.ts.net"

    if not password:
        print("Erro: KSC_PASS não definido.")
        sys.exit(1)

    setup_cmds = [
        f"echo 'EULA_ACCEPTED=1' > /tmp/ans.txt",
        f"echo 'PP_ACCEPTED=1' >> /tmp/ans.txt",
        f"echo 'KSN_ACCEPTED=1' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_TYPE=PostgreSQL' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_INSTANCE=127.0.0.1' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_PORT=5432' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_LOGIN=kluser' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_PASSWORD={db_pass}' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DB_NAME=ksc' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_TYPE=PostgreSQL' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_INSTANCE=127.0.0.1' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_PORT=5432' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_LOGIN=kluser' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_PASSWORD={db_pass}' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_DB_IAM_NAME=ksciam' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_SERVERADDRESS={fqdn}' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_IAM_ADDRESS=127.0.0.1' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_KLSVCUSER=ksc' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_KLADMINSGROUP=kladmins' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_KLIAMUSER=ksc' >> /tmp/ans.txt",
        f"echo 'KLSRV_UNATT_KLSRVUSER=ksc' >> /tmp/ans.txt",
        "sudo -E bash -c 'KLAUTOANSWERS=/tmp/ans.txt /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl'",
        "rm -f /tmp/ans.txt",
    ]

    results = run_ssh_commands_with_sudo(host, user, password, setup_cmds)
    if results:
        for res in results:
            print(
                f"CMD: {res['command']}\nSTATUS: {res['exit_status']}\nOUT: {res['stdout']}\nERR: {res['stderr']}"
            )


if __name__ == "__main__":
    main()
