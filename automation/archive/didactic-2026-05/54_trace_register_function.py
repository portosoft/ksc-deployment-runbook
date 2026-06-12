#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 54: RASTREAMENTO DE FUNÇÕES EM SCRIPTS DE SISTEMA
---------------------------------------------------------------
Este script ensina como localizar a definição de uma função (subroutine)
e ler o seu conteúdo para entender a lógica de execução.

Por que isso é importante?
Ao descobrir que 'klserver_register' é a função chave, precisamos ver o que
ela faz. No Perl, as funções começam com 'sub'. Localizar a linha exata e
ler o bloco de código permite identificar quais binários são chamados e
quais parâmetros são passados para o banco de dados.

Conceitos-chave:
1. grep -n: Localizar o padrão e retornar o número da linha.
2. Análise de Bloco de Código: Ler as instruções contidas em uma função.
3. Descoberta de Execução: Ver como a aplicação "se registra" no sistema.
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

        path = "/opt/kaspersky/ksc64/lib/bin/setup/appdata.pm"
        target_func = "klserver_register"

        print(f"Localizando a função '{target_func}' em {path}...")
        cmd_find = f'sudo -S grep -n "sub {target_func}" "{path}"'

        stdin, stdout, stderr = client.exec_command(cmd_find)
        stdin.write(password + "\n")
        stdin.flush()

        line_info = stdout.read().decode().strip()
        if line_info:
            line_num = line_info.split(":")[0]
            print(f"Função encontrada na linha {line_num}. Lendo bloco...")

            # Lemos 100 linhas a partir da definição da função
            cmd_read = f'sudo -S sed -n "{line_num},+100p" "{path}"'
            stdin_r, stdout_r, stderr_r = client.exec_command(cmd_read)
            stdin_r.write(password + "\n")
            stdin_r.flush()
            print(f"--- Código da função {target_func} ---")
            print(stdout_r.read().decode())
        else:
            print(f"Função '{target_func}' não encontrada.")

        client.close()
    except Exception as e:
        print(f"Erro no rastreamento de função: {e}")


if __name__ == "__main__":
    main()
