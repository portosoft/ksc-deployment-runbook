#!/usr/bin/env python3
import os
import sys
import paramiko
from dotenv import load_dotenv


def reconfigure_ksc_service():
    # Carregar variáveis de ambiente de forma segura
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    db_pass = os.getenv("KSC_DB_PASS")
    fqdn = os.getenv("KSC_FQDN", host)
    admin_user = os.getenv("KSC_ADMIN_USER", "KLAdmins")
    admin_pass = os.getenv("KSC_ADMIN_PASS")

    if not all([host, user, password, db_pass, admin_pass]):
        print("ERROR: Variáveis de ambiente obrigatórias ausentes no .env")
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        print("--- Gerando arquivo de respostas KLAUTOANSWERS ---")
        ans_content = f"""EULA_ACCEPTED=1
PP_ACCEPTED=1
KSN_ACCEPTED=1
KLSRV_UNATT_DBMS_TYPE=Postgres
KLSRV_UNATT_DBMS_INSTANCE=127.0.0.1
KLSRV_UNATT_DBMS_PORT=5432
KLSRV_UNATT_DBMS_LOGIN=kluser
KLSRV_UNATT_DBMS_PASSWORD={db_pass}
KLSRV_UNATT_DB_NAME=ksc
KLSRV_UNATT_DBMS_IAM_TYPE=Postgres
KLSRV_UNATT_DBMS_IAM_INSTANCE=127.0.0.1
KLSRV_UNATT_DBMS_IAM_PORT=5432
KLSRV_UNATT_DBMS_IAM_LOGIN=kluser
KLSRV_UNATT_DBMS_IAM_PASSWORD={db_pass}
KLSRV_UNATT_DB_IAM_NAME=ksciam
KLSRV_UNATT_SERVERADDRESS={fqdn}
KLSRV_UNATT_IAM_ADDRESS=127.0.0.1
KLSRV_UNATT_KLSVCUSER=ksc
KLSRV_UNATT_KLADMINSGROUP=kladmins
KLSRV_UNATT_KLIAMUSER=ksc
KLSRV_UNATT_KLSRVUSER=ksc
KLSRV_UNATT_KLADMINS_USER={admin_user}
KLSRV_UNATT_KLADMINS_PASSWORD={admin_pass}
"""
        sftp = client.open_sftp()
        with sftp.file("/tmp/reconfig_ans.txt", "w") as f:
            f.chmod(0o600)  # Prevent TOCTOU password exposure
            f.write(ans_content)
        sftp.close()

        print("--- Executando postinstall.pl (Modo Automático) ---")
        cmd = (
            "sudo -S -E bash -c "
            "'KLAUTOANSWERS=/tmp/reconfig_ans.txt "
            "/opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl'"
        )
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()

        # Stream output to console
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line.strip())

        print(stderr.read().decode())
        client.exec_command("rm -f /tmp/reconfig_ans.txt")

        print("--- Reiniciando serviços principais ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart kladminserver_srv.service ksc-web-console.service"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()
        # Wait for the command to finish to ensure restart is complete
        stdout.channel.recv_exit_status()

        client.close()
        print("--- Reconfiguração concluída ---")
    except Exception as e:
        print(f"ERROR: Falha na reconfiguração: {e}")


if __name__ == "__main__":
    reconfigure_ksc_service()
