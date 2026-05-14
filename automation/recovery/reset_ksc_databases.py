#!/usr/bin/env python3
import os
import sys
import paramiko
from dotenv import load_dotenv

def reset_all_dbs():
    # Carregar variáveis de ambiente de forma segura
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv('KSC_HOST')
    user = os.getenv('KSC_USER')
    password = os.getenv('KSC_PASS')

    if not all([host, user, password]):
        print("ERROR: Variáveis de ambiente KSC_HOST, KSC_USER ou KSC_PASS ausentes.")
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        print(f"--- Parando serviços KSC em {host} ---")
        client.exec_command(f"echo {password} | sudo -S systemctl stop kladminserver_srv ksc-web-console kliam_srv")

        print("--- Resetando bancos ksc e ksciam (Postgres) ---")
        for db in ["ksc", "ksciam"]:
            # Terminar conexões ativas para permitir o DROP
            cmd0 = f"echo {password} | sudo -S -u postgres psql -c \"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{db}' AND pid <> pg_backend_pid();\""
            client.exec_command(cmd0)

            # Drop Database
            cmd1 = f"echo {password} | sudo -S -u postgres psql -c \"DROP DATABASE {db};\""
            stdin, stdout, stderr = client.exec_command(cmd1)
            print(f"Drop {db}: {stdout.read().decode().strip()}")

            # Recreate Database
            cmd2 = f"echo {password} | sudo -S -u postgres psql -c \"CREATE DATABASE {db} OWNER kluser;\""
            stdin, stdout, stderr = client.exec_command(cmd2)
            print(f"Create {db}: {stdout.read().decode().strip()}")

        print("--- Bancos de dados reinicializados com sucesso ---")
        client.close()
    except Exception as e:
        print(f"ERROR: Falha ao conectar ou executar reset: {e}")

if __name__ == "__main__":
    reset_all_dbs()
