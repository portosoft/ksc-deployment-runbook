#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 13: INVESTIGAÇÃO DE ESQUEMAS ALTERNATIVOS
-------------------------------------------------------
Este script ensina como realizar uma busca por objetos em esquemas diferentes
do esperado (como o esquema 'public').

Por que isso é importante?
Muitas aplicações de terceiros (como o Ory Hydra usado no KSC) provisionam suas
tabelas no esquema 'public' por padrão. Se você procurar apenas no esquema
'iam' e ele estiver vazio, poderá achar erroneamente que o banco está quebrado.
Uma busca exaustiva evita conclusões precipitadas.

Conceitos-chave:
1. Search Path: O caminho que o Postgres usa para procurar tabelas.
2. Cross-Schema Audit: Validar todos os locais possíveis de armazenamento.
3. Localização de Entidades: Encontrar tabelas de suporte (como as do Hydra).
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

        print(f"Buscando tabelas no esquema 'public' do banco \"{db_name}\"...")
        # Lista tabelas no esquema public para conferência
        q = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_catalog = 'ksciam' AND table_type = 'BASE TABLE';"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Tabelas no Schema Public ---")
            print(results)
        else:
            print("Nenhuma tabela encontrada no esquema public.")

        client.close()
    except Exception as e:
        print(f"Erro na busca: {e}")


if __name__ == "__main__":
    main()
