#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 51: INSPEÇÃO DE CÓDIGO DE SCRIPTS ADMINISTRATIVOS
---------------------------------------------------------------
Este script ensina como ler o código fonte de scripts Perl (.pl) para
extrair lógica de configuração sem precisar executá-los.

Por que isso é importante?
Muitas ferramentas de infraestrutura são "caixas-pretas" que não fornecem
boa documentação. Ler as primeiras linhas de código (onde geralmente ficam
as definições de variáveis e os parsers de argumentos) é uma técnica avançada
de "white-box troubleshooting". Isso permite que você saiba exatamente o que
o script espera receber como entrada.

Conceitos-chave:
1. head -n 100: Ler o início de um arquivo para análise de cabeçalho.
2. White-box Troubleshooting: Diagnosticar problemas lendo o código fonte.
3. Análise de Lógica de Setup: Entender como o script decide o tipo de banco.
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

        path = "/opt/kaspersky/ksc64/lib/bin/setup/ksc_setup.pl"
        print(f"Lendo cabeçalho de {path}...")
        # Comando para ler as primeiras 100 linhas
        cmd = f'sudo -S head -n 100 "{path}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Início do Script Perl ---")
            print(results)
        else:
            print("Não foi possível ler o arquivo.")

        client.close()
    except Exception as e:
        print(f"Erro na inspeção do código: {e}")


if __name__ == "__main__":
    main()
