#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 37: AUDITORIA DE BIBLIOTECAS E CARREGAMENTO DE MÓDULOS
--------------------------------------------------------------------
Este script ensina como verificar se as bibliotecas de funções (.so)
estão presentes e se foram carregadas pelo servidor.

Por que isso é importante?
As bibliotecas compartilhadas são como as "peças de reposição" que o binário
principal usa. Se a biblioteca do IAM (ex: libiam.so) estiver corrompida ou
ausente, o servidor não conseguirá inicializar a lógica de identidade.
Rastrear o "Load" nos logs confirma se o servidor tentou e conseguiu
carregar essas peças.

Conceitos-chave:
1. Shared Libraries (.so): Arquivos que contêm código usado por vários programas.
2. Log Grepping: Procurar por eventos de carregamento de módulos.
3. Integridade de Software: Garantir que todos os arquivos necessários estão no lugar.
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

        print("Buscando bibliotecas do IAM em /opt/kaspersky/ksc64/lib/...")
        # Procura por arquivos que começam com libiam
        cmd_lib = "ls -F /opt/kaspersky/ksc64/lib/libiam* 2>/dev/null"
        stdin_l, stdout_l, stderr_l = client.exec_command(cmd_lib)
        print("--- Bibliotecas Encontradas ---")
        print(stdout_l.read().decode())

        print("Rastreando carregamento de plugins no log do servidor...")
        # Busca por mensagens de carregamento nos logs
        cmd_log = 'sudo -S grep -i "Load plugin" /var/log/kaspersky/ak_server.log | tail -n 20'
        stdin_log, stdout_log, stderr_log = client.exec_command(cmd_log)
        stdin_log.write(password + "\n")
        stdin_log.flush()
        print("--- Eventos de Carregamento ---")
        print(stdout_log.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro na auditoria de bibliotecas: {e}")


if __name__ == "__main__":
    main()
