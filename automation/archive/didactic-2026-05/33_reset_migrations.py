#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 33: RESET DE ESTADO DE MIGRAÇÃO (FORCE PROVISIONING)
------------------------------------------------------------------
Este script ensina como limpar a tabela de controle de migrações para forçar
a aplicação a re-provisionar sua estrutura de banco de dados.

Por que isso é importante?
Quando uma migração falha ou fica marcada como "suja" (dirty), a aplicação
para de tentar atualizar o banco. Ao dar um 'TRUNCATE' na tabela de migrações,
estamos "apagando a memória" da aplicação, forçando-a a ler todos os seus
scripts internos e criar as tabelas que estão faltando.

Conceitos-chave:
1. TRUNCATE: Comando SQL que esvazia uma tabela instantaneamente.
2. Forçar Provisionamento: Técnica de recuperação quando o setup trava.
3. Reset de Estado: Retornar a aplicação ao ponto de "instalação inicial" no banco.
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

        print(
            f'Limpando tabela de migrações no banco "{db_name}" para forçar reparo...'
        )
        # Comando para esvaziar a tabela de controle
        q = "TRUNCATE public.schema_migrations;"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print(f"Resultado: {stdout.read().decode().strip()}")

        print("Reiniciando serviço kliam_srv para disparar provisionamento...")
        client.exec_command("sudo -S systemctl restart kliam_srv")

        client.close()
    except Exception as e:
        print(f"Erro no reset de migrations: {e}")


if __name__ == "__main__":
    main()
