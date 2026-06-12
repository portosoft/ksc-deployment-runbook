#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 06: AUDITORIA DE EXTENSÕES DO BANCO DE DADOS
----------------------------------------------------------
Este script ensina como listar as extensões instaladas em um banco de dados.

Por que isso é importante?
Muitas aplicações modernas (incluindo o KSC) dependem de extensões do Postgres
para funcionalidades como criptografia, geração de UUIDs ou suporte a
procedimentos avançados. Se uma extensão necessária estiver ausente, o
provisionamento das tabelas falhará silenciosamente.

Conceitos-chave:
1. pg_extension: Tabela de catálogo que rastreia módulos instalados.
2. Dependência de Software: Validar se o "motor" do banco tem as peças necessárias.
3. psql -d: Conectar a um banco específico para realizar a auditoria.
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

        print(f'Consultando extensões instaladas no banco "{db_name}"...')
        q = "SELECT extname, extversion FROM pg_extension;"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print("--- Extensões Ativas ---")
        print(stdout.read().decode().strip())

        client.close()
    except Exception as e:
        print(f"Erro ao auditar extensões: {e}")


if __name__ == "__main__":
    main()
