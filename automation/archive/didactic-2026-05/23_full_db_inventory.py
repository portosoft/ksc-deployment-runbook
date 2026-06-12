#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 23: INVENTÁRIO MULTI-ESQUEMA EXAUSTIVO
----------------------------------------------------
Este script ensina como obter a lista completa de todas as tabelas em todos
os esquemas do banco de dados, exceto os esquemas de sistema do Postgres.

Por que isso é importante?
Em sistemas "espalhados" como o KSC, a funcionalidade de identidade pode estar
dividida em vários módulos (locker, scope, voltron). Se você olhar apenas para
o esquema 'iam', terá uma visão parcial. O inventário exaustivo permite
mapear a arquitetura real de armazenamento da aplicação.

Conceitos-chave:
1. Filtragem de Esquemas de Sistema: Ignorar 'pg_catalog' e 'information_schema'.
2. Agrupamento por Esquema: Organizar a saída para facilitar a leitura.
3. Engenharia Reversa de Banco: Entender como a aplicação organiza seus dados.
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
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)

        print(f'Gerando inventário exaustivo de tabelas em "{db_name}"...')
        # Consulta para listar todas as tabelas e seus respectivos esquemas
        q = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_catalog = 'ksciam'
          AND table_type = 'BASE TABLE'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name;
        """
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Inventário Completo (Schema | Tabela) ---")
            print(results)
        else:
            print("Nenhuma tabela encontrada no banco.")

        client.close()
    except Exception as e:
        print(f"Erro no inventário exaustivo: {e}")


if __name__ == "__main__":
    main()
