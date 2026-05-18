#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 31: DIAGNÓSTICO DE ERROS DE BANCO DE DADOS
--------------------------------------------------------
Este script ensina como buscar erros específicos de execução SQL no log
centralizado do servidor.

Por que isso é importante?
Quando uma aplicação tenta criar uma tabela e falha, o erro é registrado no
log do banco de dados (Postgres). Ao filtrar por 'ERROR', podemos descobrir
se a falha ocorreu por falta de permissão, espaço em disco (que já checamos)
ou uma inconsistência de esquema que o binário não conseguiu resolver sozinho.

Conceitos-chave:
1. journalctl -u postgresql-14: Acessar os logs da instância do Postgres.
2. Filtragem de Erros: Isolar apenas as falhas (ERROR/FATAL).
3. Correlação de Eventos: Saber o que o banco "sentiu" quando a aplicação tentou subir.
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
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        print("Buscando erros no log do Postgres (últimos 30 minutos)...")
        # Busca erros no log do Postgres. Nota: o nome do serviço pode variar (postgresql, postgresql-14, etc)
        cmd = 'sudo -S journalctl -u postgresql* --since "30 minutes ago" | grep -i "error" | tail -n 20'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            # Limpeza ASCII para Windows
            clean_text = "".join(c for c in results if ord(c) < 128)
            print("--- Erros Encontrados no Postgres ---")
            print(clean_text)
        else:
            print("Nenhum erro recente encontrado no log do Postgres.")

        client.close()
    except Exception as e:
        print(f"Erro na auditoria do banco: {e}")


if __name__ == "__main__":
    main()
