#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 52: ENGENHARIA REVERSA DE MÓDULOS DE SISTEMA (.PM)
----------------------------------------------------------------
Este script ensina como analisar o conteúdo de bibliotecas de funções
em Perl (arquivos .pm) para extrair lógica de configuração complexa.

Por que isso é importante?
Diferente de scripts executáveis, os módulos (.pm) contêm as definições de
funções que o software usa repetidamente. Ao ler o 'appdata.pm', podemos
descobrir como o KSC valida a integridade do banco de dados e quais
comandos ele executa para criar o esquema do IAM. Isso nos permite replicar
esses comandos manualmente para forçar o reparo.

Conceitos-chave:
1. Perl Modules (.pm): Arquivos que armazenam funções reutilizáveis.
2. Análise de Fluxo de Dados: Seguir a lógica de uma função (ex: app_register).
3. Descoberta de Comandos Ocultos: Encontrar as chamadas de sistema que o KSC faz.
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
        print(f"Lendo conteúdo de {path}...")
        # Lemos uma parte maior do arquivo para encontrar as funções
        cmd = f'sudo -S head -n 300 "{path}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Conteúdo de appdata.pm ---")
            print(results)
        else:
            print("Não foi possível ler o arquivo.")

        client.close()
    except Exception as e:
        print(f"Erro na análise do módulo: {e}")


if __name__ == "__main__":
    main()
