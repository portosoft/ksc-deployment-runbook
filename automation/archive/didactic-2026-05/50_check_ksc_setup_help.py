#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 50: INVESTIGAÇÃO DE SCRIPTS PERL DE INSTALAÇÃO
------------------------------------------------------------
Este script ensina como investigar scripts de automação em Perl (extensão .pl)
que são usados para configurar servidores corporativos.

Por que isso é importante?
Scripts Perl são a "espinha dorsal" de muitos instaladores de software Linux.
Diferente de binários compilados, eles são scripts de texto que chamam outros
processos. Consultar a ajuda do 'ksc_setup.pl' pode revelar comandos de
reinstalação ou re-configuração de banco que não estão documentados no
manual básico.

Conceitos-chave:
1. Perl Scripts (.pl): Linguagem comum para automação de infraestrutura.
2. Comandos de Manutenção de Instalação: Ferramentas para reparar o software.
3. Descoberta de Parâmetros de Setup: Identificar flags de banco de dados.
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

        setup_script = "/opt/kaspersky/ksc64/lib/bin/setup/ksc_setup.pl"
        print(f"Consultando ajuda de {setup_script}...")

        # Comando para ver as opções do script Perl
        cmd = f"sudo -S {setup_script} --help"

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Opções de ksc_setup.pl ---")
            print(results)
        else:
            print(
                "Não foi possível obter a ajuda do script (possivelmente não aceita --help)."
            )

        client.close()
    except Exception as e:
        print(f"Erro na investigação do setup: {e}")


if __name__ == "__main__":
    main()
