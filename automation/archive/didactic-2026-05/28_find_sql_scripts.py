#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 28: LOCALIZAÇÃO DE SCRIPTS DE DEFINIÇÃO DE DADOS (DDL)
--------------------------------------------------------------------
Este script ensina como localizar os arquivos SQL originais que a aplicação
usa para criar a sua estrutura de banco de dados.

Por que isso é importante?
Se o provisionamento automático falhou, a forma mais garantida de resolver
é encontrar o script SQL que cria as tabelas e executá-lo manualmente.
Saber onde esses scripts "moram" é vital para qualquer recuperação de
desastre em sistemas de banco de dados.

Conceitos-chave:
1. find -name "*.sql": Localizar todos os scripts SQL em uma árvore de diretórios.
2. DDL (Data Definition Language): Scripts que definem tabelas, índices e esquemas.
3. Recuperação Manual: Executar scripts de sistema quando a automação falha.
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

        base_path = "/opt/kaspersky/ksc64/"
        print(f"Buscando scripts SQL em {base_path}...")

        # Comando para encontrar todos os arquivos .sql recursivamente
        cmd = f'sudo -S find "{base_path}" -name "*.sql"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Scripts SQL Encontrados ---")
            print(results)
        else:
            print("Nenhum script SQL encontrado no diretório da aplicação.")

        client.close()
    except Exception as e:
        print(f"Erro na busca de scripts: {e}")


if __name__ == "__main__":
    main()
