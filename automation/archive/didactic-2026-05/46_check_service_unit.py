#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 46: AUDITORIA DE UNIDADE DE SERVIÇO (SYSTEMCTL CAT)
------------------------------------------------------------------
Este script ensina como visualizar o arquivo de unidade (.service) que
define como o Systemd inicia a aplicação.

Por que isso é importante?
A unidade de serviço contém o comando exato (ExecStart) que inicia o binário.
Lá podemos ver quais flags de configuração são passadas e quais variáveis
de ambiente são definidas. Se o serviço está apontando para um diretório de
configuração antigo, descobriremos isso lendo a unidade.

Conceitos-chave:
1. systemctl cat: Mostra a definição completa da unidade de serviço.
2. ExecStart: A linha de comando que inicia a aplicação.
3. Environment: Variáveis de sistema que podem mudar o comportamento do binário.
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

        service = "kliam_srv"
        print(f'Lendo definição da unidade de serviço "{service}"...')
        # Comando para mostrar a unidade do serviço
        cmd = f'systemctl cat "{service}"'

        stdin, stdout, stderr = client.exec_command(cmd)

        results = stdout.read().decode().strip()
        if results:
            print(f"--- Definição de {service} ---")
            print(results)
        else:
            print(f'Unidade de serviço "{service}" não encontrada.')

        client.close()
    except Exception as e:
        print(f"Erro na auditoria da unidade: {e}")


if __name__ == "__main__":
    main()
