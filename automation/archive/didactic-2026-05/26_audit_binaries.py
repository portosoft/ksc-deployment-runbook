#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 26: AUDITORIA DE BINÁRIOS DE SISTEMA
--------------------------------------------------
Este script ensina como listar os executáveis disponíveis no diretório
da aplicação para identificar ferramentas de suporte ou serviços ocultos.

Por que isso é importante?
Muitas vezes, a solução não está no serviço principal, mas em um utilitário de
ajuda (helper) ou em um binário de manutenção que o administrador deve
rodar para concluir a instalação. Conhecer os binários disponíveis é como
conhecer as ferramentas na sua caixa de ferramentas.

Conceitos-chave:
1. ls -F: Lista arquivos identificando executáveis com um asterisco (*).
2. Binários de Sistema (sbin): Onde residem os executáveis de administração.
3. Engenharia Reversa de Componentes: Entender a arquitetura pelos seus binários.
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

        print("Listando binários em /opt/kaspersky/ksc64/sbin/...")
        # Comando para listar arquivos executáveis
        cmd = "ls -F /opt/kaspersky/ksc64/sbin/"

        stdin, stdout, stderr = client.exec_command(cmd)

        results = stdout.read().decode().strip()
        if results:
            print("--- Binários Encontrados ---")
            print(results)
        else:
            print("Nenhum binário encontrado no diretório sbin.")

        client.close()
    except Exception as e:
        print(f"Erro na auditoria de binários: {e}")


if __name__ == "__main__":
    main()
