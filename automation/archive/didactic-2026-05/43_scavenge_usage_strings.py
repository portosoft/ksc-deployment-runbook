#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 43: GARIMPAGEM DE USO (STRINGS & CONTEXTO)
--------------------------------------------------------
Este script ensina como extrair manuais de uso embutidos em binários usando
busca por padrões com contexto (After/Before).

Por que isso é importante?
Muitos programas Go/C++ incluem strings de exemplo de uso que começam com
'Usage:'. Ao usar 'grep -A', capturamos as linhas que vêm logo após esse termo,
revelando os argumentos secretos que o comando '--help' não mostrou por
causa de um erro prematuro.

Conceitos-chave:
1. grep -A <N>: Mostrar as N linhas seguintes após o casamento do padrão.
2. Engenharia de Texto em Binários: Reconstruir o manual a partir das strings.
3. Descoberta de Argumentos: Identificar flags como --db-type ou --dsn.
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

        binary_path = "/opt/kaspersky/ksc64/sbin/kliam"
        print(f"Garimpando instruções de uso em {binary_path}...")

        # Busca pelo termo Usage e mostra as 5 linhas seguintes
        cmd = f'sudo -S strings "{binary_path}" | grep -iA 5 "Usage:"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Blocos de Uso Encontrados ---")
            print(results)
        else:
            print("Nenhuma instrução 'Usage' encontrada no binário.")

        client.close()
    except Exception as e:
        print(f"Erro na garimpagem: {e}")


if __name__ == "__main__":
    main()
