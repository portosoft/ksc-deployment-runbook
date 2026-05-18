#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 12: DIAGNÓSTICO VIA JOURNALCTL (SYSTEMD)
-------------------------------------------------------
Este script ensina como extrair informações do log central do sistema Linux
(Journal), ignorando arquivos de log individuais.

Por que isso é importante?
Muitas falhas críticas de inicialização (como erros de kernel ou crashes de
binário) ocorrem ANTES do serviço conseguir abrir seu próprio arquivo de log.
Nesses casos, o Journalctl é a única fonte da verdade, pois captura a saída
direta (stdout/stderr) gerenciada pelo Systemd.

Conceitos-chave:
1. Journalctl: O log centralizado moderno do Linux (Substituto do syslog).
2. Filtragem Temporal (--since): Focar apenas no que aconteceu recentemente.
3. Diagnóstico de Causa Raiz: Ver erros que não aparecem nos logs da aplicação.
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

        print("Consultando o Journal do Systemd para serviços KSC/KL...")
        # Filtra logs dos últimos 10 minutos para serviços específicos
        cmd = (
            'sudo -S journalctl -u "kl*" -u "KSC*" --since "10 minutes ago" --no-pager'
        )

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Mensagens do Journal Encontradas ---")
            print(results)
        else:
            print("Nenhuma mensagem recente encontrada no Journal.")

        client.close()
    except Exception as e:
        print(f"Erro na consulta do Journal: {e}")


if __name__ == "__main__":
    main()
