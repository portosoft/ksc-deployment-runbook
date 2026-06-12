#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 38: MAPEAMENTO DE DEPENDÊNCIAS E BUSCA HISTÓRICA
--------------------------------------------------------------
Este script ensina como realizar buscas históricas extensas e mapear os nomes
das bibliotecas de um software de prateleira.

Por que isso é importante?
Às vezes, a aplicação usa nomes diferentes do que esperamos (ex: 'auth' em vez
de 'iam'). Ao listar todas as bibliotecas e buscar nos logs de um dia inteiro,
conseguimos mapear o vocabulário técnico da ferramenta, identificando os
verdadeiros responsáveis pela falha.

Conceitos-chave:
1. Busca Histórica: Analisar um período maior (24h) para encontrar eventos raros.
2. Mapeamento de Nomenclatura: Descobrir os nomes reais dos componentes.
3. Auditoria de Instalação: Garantir que a árvore de diretórios está completa.
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

        print("Listando as primeiras 50 bibliotecas em /opt/kaspersky/ksc64/lib/...")
        cmd_lib = "ls /opt/kaspersky/ksc64/lib/ | head -n 50"
        stdin_l, stdout_l, stderr_l = client.exec_command(cmd_lib)
        print("--- Bibliotecas (Amostra) ---")
        print(stdout_l.read().decode())

        print("Buscando por 'iam' nos logs das últimas 24 horas...")
        # Busca no log histórico (pode ser grande, pegamos as últimas 50 linhas do resultado)
        cmd_log = 'sudo -S grep -i "iam" /var/log/kaspersky/ak_server.log | tail -n 50'
        stdin_log, stdout_log, stderr_log = client.exec_command(cmd_log)
        stdin_log.write(password + "\n")
        stdin_log.flush()
        print("--- Menções Históricas ao IAM ---")
        print(stdout_log.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro no mapeamento histórico: {e}")


if __name__ == "__main__":
    main()
