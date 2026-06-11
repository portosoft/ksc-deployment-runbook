#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 15: AUDITORIA DE VOLUME POR ESQUEMA
-------------------------------------------------
Este script ensina como realizar uma auditoria quantitativa no banco de dados.
Ao contar o número de tabelas em cada esquema, podemos identificar se uma
área específica (como o 'iam') está vazia ou se o sistema redistribuiu
as tabelas de forma inesperada.

Por que isso é importante?
Na resolução de problemas de DevSecOps, saber o "tamanho" de cada módulo
ajuda a isolar falhas de migração de banco de dados. Se o esquema 'iam'
tiver 0 tabelas e o 'public' tiver 20, sabemos que a migração de identidade
nem sequer começou.

Conceitos-chave:
1. COUNT(*): Função de agregação para contagem de registros.
2. GROUP BY: Agrupa os resultados por uma coluna específica (table_schema).
3. Auditoria Modular: Focar em módulos lógicos para diagnosticar falhas.
"""

import os
import paramiko
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)

        print("Auditoria de densidade de tabelas por esquema no ksciam...")
        # Consulta para contar tabelas agrupadas por esquema
        q = """
        SELECT table_schema, COUNT(*)
        FROM information_schema.tables
        WHERE table_catalog = 'ksciam' AND table_type = 'BASE TABLE'
        GROUP BY table_schema
        ORDER BY table_schema;
        """
        cmd = f'sudo -S -u postgres psql -d ksciam -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Contagem por Esquema ---")
            print("Esquema | Tabelas")
            print(results)
        else:
            print("Nenhum dado encontrado.")

        client.close()
    except Exception as e:
        print(f"Erro na auditoria de volume: {e}")


if __name__ == "__main__":
    main()
