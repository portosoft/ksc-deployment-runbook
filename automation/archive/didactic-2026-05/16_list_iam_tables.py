#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 16: INVENTÁRIO NOMINAL DE TABELAS
-----------------------------------------------
Este script ensina como realizar um inventário detalhado de objetos no banco.
Ao listar os nomes das tabelas, podemos comparar com listas de referências
(baselines) para saber quais funcionalidades foram provisionadas.

Por que isso é importante?
Na engenharia de sistemas, às vezes o número de tabelas (ex: 17) é o mesmo,
mas as tabelas em si são diferentes. Listar os nomes é a única forma de
garantir que as entidades de negócio (identidades, usuários, etc) foram
realmente criadas.

Conceitos-chave:
1. Inventário de Objetos: Essencial para auditorias de conformidade.
2. Comparação de Strings: Usado para validar o progresso de scripts de setup.
3. Filtros ANSI SQL: Usar table_schema para isolar componentes.
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

        print("Gerando inventário nominal do esquema 'iam' no ksciam...")
        # Consulta para listar nomes de tabelas em ordem alfabética
        q = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'iam' AND table_catalog = 'ksciam' ORDER BY table_name;"
        cmd = f'sudo -S -u postgres psql -d ksciam -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Inventário do Esquema IAM ---")
            print(results)
        else:
            print("Nenhuma tabela encontrada no esquema IAM.")

        client.close()
    except Exception as e:
        print(f"Erro no inventário: {e}")


if __name__ == "__main__":
    main()
