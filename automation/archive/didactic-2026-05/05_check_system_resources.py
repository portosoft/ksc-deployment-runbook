#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 05: MONITORAMENTO DE RECURSOS FÍSICOS
----------------------------------------------------
Este script demonstra como automatizar o monitoramento da saúde do servidor,
focando no espaço em disco das partições críticas.

Por que isso é importante?
Bancos de dados e logs crescem constantemente. Se a partição /var (onde o
Postgres armazena os dados) ficar cheia, o banco parará de funcionar e
corromperá os dados. Monitorar isso via script previne desastres.

Conceitos-chave:
1. df -h: Comando Linux para listar o uso do sistema de arquivos de forma legível.
2. grep -E: Filtra apenas as partições que nos interessam (/, /var, /opt).
3. Monitoramento de Infraestrutura: Automatizar checagens periódicas de saúde.
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

        print("Auditando espaço em disco nas partições do sistema...")
        # Comando para verificar as partições mais importantes para o KSC
        cmd = 'df -h | grep -E "Filesystem|/var|/opt|/home|/"'

        stdin, stdout, stderr = client.exec_command(cmd)

        print("--- Relatório de Espaço em Disco ---")
        print(stdout.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro ao auditar recursos: {e}")


if __name__ == "__main__":
    main()
