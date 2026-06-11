#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 27: INVESTIGAÇÃO DE FERRAMENTAS DE CONFIGURAÇÃO
-------------------------------------------------------------
Este script ensina como descobrir a finalidade de binários desconhecidos
no sistema usando comandos de ajuda e exploração de pastas.

Por que isso é importante?
Ao se deparar com uma lista de binários como 'klsrvconfig', o primeiro passo é
consultar o seu manual ou ajuda interna. Isso evita "chutes" e permite
executar comandos com precisão cirúrgica, sabendo exatamente o que cada
parâmetro faz.

Conceitos-chave:
1. --help: A flag universal para descobrir as funções de um programa.
2. Exploração Recursiva: Olhar dentro de pastas como 'rbac' para encontrar scripts.
3. Engenharia Reversa de Comandos: Aprender a usar as ferramentas do próprio software.
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

        print("Consultando ajuda do klsrvconfig...")
        cmd_help = "sudo -S /opt/kaspersky/ksc64/sbin/klsrvconfig --help"
        stdin, stdout, stderr = client.exec_command(cmd_help)
        stdin.write(password + "\n")
        stdin.flush()
        print("--- Help de klsrvconfig ---")
        print(stdout.read().decode())

        print("\nListando conteúdo do diretório rbac/...")
        cmd_rbac = "ls -F /opt/kaspersky/ksc64/sbin/rbac/"
        stdin_r, stdout_r, stderr_r = client.exec_command(cmd_rbac)
        print("--- Conteúdo de rbac/ ---")
        print(stdout_r.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro na investigação: {e}")


if __name__ == "__main__":
    main()
