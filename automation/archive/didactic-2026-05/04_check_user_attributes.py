#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 04: AUDITORIA DE ATRIBUTOS DE ROLES NO POSTGRES
-------------------------------------------------------------
Este script ensina como verificar os privilégios de alto nível (Superuser,
CreateDB, etc.) de um usuário no banco de dados.

Por que isso é importante?
Para que um serviço como o KSC consiga realizar migrações de banco ou criar
novas estruturas, o usuário configurado precisa ter os atributos corretos.
Um usuário sem permissão de criação falhará ao tentar provisionar o sistema.

Conceitos-chave:
1. pg_roles: Tabela de sistema que armazena todas as permissões globais.
2. Atributos de Role: Flags como 'rolsuper' (Superusuário) e 'rolcreatedb'.
3. Auditoria Preventiva: Validar permissões antes de iniciar instalações.
"""

import os
import paramiko
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    db_user = os.getenv("KSC_DB_USER")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)

        # Consulta para verificar os atributos da role
        q = f'SELECT rolname, rolcreatedb, rolcreaterole, rolsuper FROM pg_roles WHERE rolname = "{db_user}";'
        cmd = f'sudo -S -u postgres psql -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        result = stdout.read().decode().strip()
        print(f"Atributos da Role (Name | CreateDB | CreateRole | Superuser): {result}")

        client.close()
    except Exception as e:
        print(f"Erro na auditoria de roles: {e}")


if __name__ == "__main__":
    main()
