#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 42: INVESTIGAÇÃO DE SUB-COMANDOS (HELP RECURSIVO)
---------------------------------------------------------------
Este script ensina como obter ajuda detalhada sobre um sub-comando de um
binário (como o 'migrate' do 'kliam').

Por que isso é importante?
Binários modernos usam árvores de comandos. O 'help' geral mostra os comandos
principais, mas cada sub-comando pode ter suas próprias opções. Descobrir
como passar o tipo de banco (db type) ou a string de conexão é o que separa
um chute de uma intervenção técnica precisa.

Conceitos-chave:
1. Sub-commands: Comandos dentro de comandos (ex: kliam migrate help).
2. Argument Parsing: Entender como o programa lê os dados da linha de comando.
3. Troubleshooting de Parâmetros: Resolver erros de "missing argument" ou "failed type".
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

        # Tentamos obter ajuda específica sobre o comando migrate
        # Nota: Testamos 'help migrate' e 'migrate --help'
        cmd_help = "sudo -S /opt/kaspersky/ksc64/sbin/kliam help migrate 2>&1"

        print("Consultando ajuda detalhada do comando 'migrate'...")
        stdin, stdout, stderr = client.exec_command(cmd_help)
        stdin.write(password + "\n")
        stdin.flush()

        print("--- Ajuda do Sub-comando ---")
        print(stdout.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro na consulta de sub-comando: {e}")


if __name__ == "__main__":
    main()
