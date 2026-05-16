#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 02: GESTÃO DE ESQUEMAS E PRIVILÉGIOS SQL
------------------------------------------------------
Este script demonstra como automatizar o provisionamento de estruturas
dentro de um banco de dados Postgres usando Python.

Por que isso é importante?
Na automação de infraestrutura, precisamos garantir que o ambiente esteja
correto antes da aplicação iniciar. Criar esquemas e definir donos (owners)
programaticamente garante que a aplicação terá as permissões necessárias
para criar suas tabelas de negócio.

Conceitos-chave:
1. SCHEMA: Uma área lógica dentro do banco de dados (como uma pasta).
2. AUTHORIZATION: Define quem é o "dono" do esquema, permitindo controle total.
3. psql -c: Execução de comandos SQL diretamente via linha de comando.
"""

import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    db_name = os.getenv("KSC_IAM_NAME")
    db_user = os.getenv("KSC_DB_USER")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        # SQL para criar o esquema e dar permissões
        sql = f"CREATE SCHEMA IF NOT EXISTS iam AUTHORIZATION \"{db_user}\"; GRANT ALL ON SCHEMA iam TO \"{db_user}\";"

        print(f"Provisionando esquema 'iam' no banco \"{db_name}\"...")
        cmd = f"sudo -S -u postgres psql -d \"{db_name}\" -c \"{sql}\""

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print(f"Resultado: {stdout.read().decode().strip()}")
        client.close()
    except Exception as e:
        print(f"Erro na execução SQL: {e}")

if __name__ == "__main__":
    main()
