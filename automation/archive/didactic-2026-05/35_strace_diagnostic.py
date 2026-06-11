#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 35: RASTREAMENTO DE CHAMADAS DE SISTEMA (STRACE)
--------------------------------------------------------------
Este script ensina como realizar o diagnóstico definitivo de uma aplicação
usando o comando 'strace' para ver todas as interações com o kernel.

Por que isso é importante?
Quando os logs não dizem nada e o comportamento é inexplicável, o strace revela
a verdade. Ele mostra cada arquivo que o programa tentou abrir e cada conexão
de rede que ele tentou fazer. Se o postinstall estiver falhando silenciosamente
porque não encontra uma biblioteca ou um certificado, o strace nos dirá.

Conceitos-chave:
1. strace -e trace=file,network: Monitorar apenas chamadas de arquivo e rede.
2. Diagnóstico de Nível Profundo: Ver o que a aplicação faz, não o que ela diz.
3. Troubleshooting de "Caixa Preta": Diagnosticar programas sem código fonte.
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
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)

        print("Iniciando rastreamento (strace) do postinstall.pl...")
        # Comando para rastrear abertura de arquivos e rede.
        # Nota: Usamos timeout e pegamos as primeiras 100 linhas para não inundar o console.
        cmd = "sudo -S strace -f -e trace=openat,connect /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl 2>&1 | head -n 100"

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        # O strace gera muita saída, lemos com cuidado
        results = stdout.read().decode().strip()
        if results:
            print("--- Rastreamento de Sistema (Primeiras 100 linhas) ---")
            print(results)
        else:
            print("Nenhum dado de rastreamento capturado.")

        client.close()
    except Exception as e:
        print(f"Erro no rastreamento: {e}")


if __name__ == "__main__":
    main()
