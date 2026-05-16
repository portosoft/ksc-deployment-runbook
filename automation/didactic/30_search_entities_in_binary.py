#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 30: BUSCA DE ENTIDADES ESPECÍFICAS EM BINÁRIOS
------------------------------------------------------------
Este script ensina como realizar uma busca direcionada usando Expressões
Regulares (Regex) para encontrar entidades específicas dentro de um binário.

Por que isso é importante?
Ao invés de listar tudo, podemos focar apenas no que nos interessa (users,
identities). Se essas strings não existirem no binário 'kliam', saberemos
com certeza que ele NÃO é o responsável por criar essas tabelas, e poderemos
mover nossa investigação para outro binário (como o 'klserver').

Conceitos-chave:
1. Grep -iE: Busca insensível a maiúsculas com suporte a Regex (operador |).
2. Identificação de Responsabilidade: Descobrir qual serviço gerencia quais dados.
3. Troubleshooting de Arquitetura: Mapear as dependências entre binários e tabelas.
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
        print(f"Buscando identidades/usuários no binário {binary_path}...")

        # Busca por termos chave usando Regex
        cmd = f"sudo -S strings \"{binary_path}\" | grep -iE \"users|identities|authentication_factors\" | head -n 20"

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Menções Encontradas ---")
            print(results)
        else:
            print(f"Nenhuma menção a usuários ou identidades encontrada em {binary_path}.")

        client.close()
    except Exception as e:
        print(f"Erro na análise direcionada: {e}")

if __name__ == "__main__":
    main()
