#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 34: BUSCA DE TABELAS DE CONTROLE ESPECÍFICAS
----------------------------------------------------------
Este script ensina como localizar tabelas de metadados (como tabelas de
migração) que podem estar escondidas dentro de um esquema específico.

Por que isso é importante?
Muitas aplicações usam uma tabela de migração por "módulo". O Ory Hydra usa
a 'public.schema_migrations', mas o componente de identidade da Kaspersky
pode usar uma tabela diferente dentro do esquema 'iam' (ex: 'iam.migrations').
Encontrar essa tabela é essencial para resetar o estado de cada módulo
individualmente.

Conceitos-chave:
1. LIKE '%migration%': Busca por nomes que contenham o padrão de migração.
2. Auditoria por Módulo: Isolar as tabelas de controle de cada parte da aplicação.
3. Troubleshooting de Migrações Complexas: Lidar com múltiplos sistemas de versão.
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

        print("Buscando tabelas de migração dentro do esquema 'iam'...")
        # Consulta para localizar tabelas que sugiram controle de versão no iam
        q = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'iam' AND table_name LIKE '%migration%';"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Tabelas de Migração no IAM Encontradas ---")
            print(results)
        else:
            print("Nenhuma tabela de migração encontrada no esquema 'iam'.")

        client.close()
    except Exception as e:
        print(f"Erro na busca: {e}")


if __name__ == "__main__":
    main()
