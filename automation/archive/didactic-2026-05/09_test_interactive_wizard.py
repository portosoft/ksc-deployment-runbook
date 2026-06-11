#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 09: AUTOMAÇÃO DE COMANDOS INTERATIVOS (FLUXO DE ENTRADA)
----------------------------------------------------------------------
Este script ensina como iniciar um assistente interativo e capturar suas
instruções iniciais para planejar uma automação completa.

Por que isso é importante?
Wizards (como o postinstall.pl) são feitos para humanos. Automatizá-los
exige que saibamos exatamente o que eles perguntam e em qual ordem.
Mapear as primeiras perguntas é o passo 1 para criar um robô de preenchimento.

Conceitos-chave:
1. Timeout de Execução: Evita que o script fique preso esperando o humano.
2. Buffer de Saída (read): Ler apenas uma parte da resposta do servidor.
3. Engenharia de Reverso de Wizard: Mapear o comportamento do instalador.
"""

import os
import paramiko
import time
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

        print("Iniciando o wizard postinstall.pl para mapeamento...")
        cmd = "sudo -S LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl"

        stdin, stdout, stderr = client.exec_command(cmd)

        # Enviar senha do sudo
        stdin.write(password + "\n")
        stdin.flush()

        # Aguardar tempo para o wizard carregar
        time.sleep(5)

        # Ler os primeiros 1000 caracteres das perguntas
        output = stdout.read(1000).decode()
        print("--- Primeiras Perguntas do Wizard ---")
        print(output)

        client.close()
    except Exception as e:
        print(f"Erro no mapeamento: {e}")


if __name__ == "__main__":
    main()
