#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 25: LOCALIZAÇÃO GLOBAL DE ENTIDADES POR NOME
-----------------------------------------------------------
Este script ensina como realizar uma busca "desesperada" por tabelas específicas
em todo o banco de dados, sem se importar com o esquema.

Por que isso é importante?
Se você sabe que a aplicação PRECISA de uma tabela chamada 'users', mas não
a encontra no esquema 'iam', ela pode estar em qualquer outro lugar
(como no esquema 'public' ou 'ksc'). Esta busca global garante que você
não deixará nenhum lugar sem auditar.

Conceitos-chave:
1. Cross-Schema Searching: Buscar em todas as áreas lógicas simultaneamente.
2. IN Clause: Filtrar por múltiplos nomes de interesse (users, identities, factors).
3. Auditoria de Existência: Confirmar se o "coração" da aplicação foi provisionado.
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

        print(
            "Buscando tabelas críticas ('users', 'identities', 'authentication_factors') em todos os esquemas..."
        )
        # Consulta global por nome de tabela
        targets = "('users', 'identities', 'authentication_factors')"
        q = f"SELECT table_schema, table_name FROM information_schema.tables WHERE table_catalog = 'ksciam' AND table_name IN {targets};"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Entidades Encontradas ---")
            print("Esquema | Tabela")
            print(results)
        else:
            print(
                "ERRO CRÍTICO: Tabelas de identidade NÃO encontradas em nenhum esquema!"
            )

        client.close()
    except Exception as e:
        print(f"Erro na busca global: {e}")


if __name__ == "__main__":
    main()
