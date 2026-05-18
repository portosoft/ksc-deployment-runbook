#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 03: AUDITORIA DE PROPRIEDADE (OWNERSHIP)
------------------------------------------------------
Este script ensina como realizar auditorias de segurança em metadados do
Postgres para validar quem é o proprietário real de uma estrutura de dados.

Por que isso é importante?
Muitas falhas de "Acesso Negado" em aplicações ocorrem porque o esquema
do banco foi criado por um usuário (ex: root/postgres) e a aplicação tenta
usar outro (ex: kluser). Validar o OWNER é o primeiro passo do troubleshooting.

Conceitos-chave:
1. Catálogo do Sistema: Tabelas internas do Postgres (pg_namespace, pg_roles).
2. SQL Joins: Unir tabelas de sistema para traduzir IDs (oids) em nomes legíveis.
3. psql -t: O modo "tuples only" remove cabeçalhos da saída, facilitando o parse.
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

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        # Consulta para verificar o OWNER do esquema
        q = "SELECT nspname, rolname FROM pg_namespace n JOIN pg_roles r ON n.nspowner = r.oid WHERE nspname = 'iam';"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        result = stdout.read().decode().strip()
        print(f"Auditoria de Propriedade (Schema | Owner): {result}")

        client.close()
    except Exception as e:
        print(f"Erro na auditoria: {e}")


if __name__ == "__main__":
    main()
