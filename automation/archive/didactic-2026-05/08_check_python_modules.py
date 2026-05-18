#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 08: VERIFICAÇÃO DE DEPENDÊNCIAS DE SOFTWARE
----------------------------------------------------------
Este script ensina como validar se as ferramentas de automação (módulos
Python) estão presentes no servidor remoto.

Por que isso é importante?
Antes de rodar um script complexo que dependa de bibliotecas externas
(como pexpect ou requests), devemos verificar se elas existem. Tentar
rodar um script sem as dependências causará erros de execução que podem
ser difíceis de depurar em grandes fluxos.

Conceitos-chave:
1. Module Discovery: Usar o interpretador para testar a presença de módulos.
2. Error Handling: Capturar o Traceback de erro para entender o que falta.
3. Pré-requisitos de Automação: Validar o ambiente antes da execução principal.
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

        print("Verificando disponibilidade do módulo 'pexpect' no servidor...")
        # Testa a importação do módulo via linha de comando
        cmd = (
            "python3 -c \"import pexpect; print('SUCCESS: pexpect is installed')\" 2>&1"
        )

        stdin, stdout, stderr = client.exec_command(cmd)

        result = stdout.read().decode().strip()
        if "SUCCESS" in result:
            print(f"Resultado: {result}")
        else:
            print("Resultado: pexpect NÃO encontrado. Usaremos métodos alternativos.")
            print(f"Erro bruto para estudo: {result}")

        client.close()
    except Exception as e:
        print(f"Erro na verificação: {e}")


if __name__ == "__main__":
    main()
