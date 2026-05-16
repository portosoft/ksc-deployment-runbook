#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 55: BUSCA DE USUÁRIO ADMINISTRADOR ESPECÍFICO
------------------------------------------------------------
Este script ensina como realizar uma busca filtrada por um nome de
usuário específico no banco de dados de identidade.

Por que isso é importante?
Agora que sabemos que o administrador deve ser 'kscadmin', precisamos
confirmar se ele já foi provisionado pelo sistema ou se o banco está
vazio. Se o resultado for zero, saberemos que o problema de restauração
do banco persiste e que precisamos forçar a criação deste usuário.

Conceitos-chave:
1. Filtro SQL (WHERE name = '...'): Localizar um registro exato.
2. Auditoria de Existência: Confirmar se a conta mestre está ativa.
3. Troubleshooting de Login: Validar a base de dados antes de tentar o acesso.
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
    admin_name = os.getenv("KSC_ADMIN_NAME")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        print(f'Buscando o usuário "{admin_name}" no banco IAM...')
        # Consulta filtrada pelo nome do administrador
        q = f"SELECT name, id FROM iam.users WHERE name = '{admin_name}';"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print(f"--- Usuário '{admin_name}' Encontrado ---")
            print(results)
        else:
            print(f"O usuário '{admin_name}' NÃO existe no banco IAM.")

        client.close()
    except Exception as e:
        print(f"Erro na busca de administrador: {e}")


if __name__ == "__main__":
    main()
