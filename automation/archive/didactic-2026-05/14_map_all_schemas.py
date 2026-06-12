#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 14: MAPEAMENTO GLOBAL DE ESQUEMAS
-----------------------------------------------
Este script ensina como realizar uma busca exaustiva por todos os esquemas
disponíveis em um banco de dados Postgres.

Por que isso é importante?
Em sistemas complexos como o KSC, diferentes componentes da aplicação
podem criar suas tabelas em esquemas distintos (ex: 'public', 'iam', 'scope').
Mapear esses esquemas é o primeiro passo para localizar dados "perdidos"
ou entender falhas de provisionamento onde tabelas aparecem em locais inesperados.

Conceitos-chave:
1. information_schema.tables: Tabela padrão ANSI para metadados.
2. DISTINCT: Garante que cada nome de esquema apareça apenas uma vez.
3. table_catalog: Filtra a busca para o banco de dados específico (ksciam).
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
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)

        print("Mapeando todos os esquemas ativos no banco ksciam...")
        # Consulta para listar esquemas únicos que possuem tabelas base
        q = "SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_catalog = 'ksciam' ORDER BY table_schema;"
        cmd = f'sudo -S -u postgres psql -d ksciam -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Esquemas com Tabelas Encontrados ---")
            print(results)
        else:
            print("Nenhum esquema com tabelas encontrado.")

        client.close()
    except Exception as e:
        print(f"Erro no mapeamento global: {e}")


if __name__ == "__main__":
    main()
