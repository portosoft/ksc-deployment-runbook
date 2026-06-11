#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 32: AUDITORIA DE VERSÃO DE ESQUEMA (MIGRATIONS)
-------------------------------------------------------------
Este script ensina como verificar a tabela de controle de migrações
(schema_migrations) para entender o estado evolutivo do banco de dados.

Por que isso é importante?
Frameworks de banco de dados usam uma tabela de controle para saber quais
scripts de criação já foram executados. Se essa tabela contiver uma versão
que não condiz com a realidade das tabelas existentes, a aplicação "achará"
que tudo está pronto e não criará o que falta. Resetar essa tabela costuma
ser a chave para forçar um re-provisionamento.

Conceitos-chave:
1. schema_migrations: Tabela padrão de controle de versão de banco.
2. Migração de Dados: O processo de evoluir a estrutura do banco.
3. Auditoria de Estado: Validar a percepção da aplicação sobre o banco.
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
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)

        print(f'Consultando tabela de migrações no banco "{db_name}"...')
        # Consulta para ver as versões registradas na migração
        q = "SELECT * FROM public.schema_migrations;"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Versões de Migração Registradas ---")
            print(results)
        else:
            print("Tabela schema_migrations está vazia ou não existe.")

        client.close()
    except Exception as e:
        print(f"Erro na auditoria de migrations: {e}")


if __name__ == "__main__":
    main()
