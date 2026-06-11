#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 47: AUDITORIA DE CARACTERES INVISÍVEIS (CAT -A)
-------------------------------------------------------------
Este script ensina como expor caracteres de controle ocultos (como tabs,
quebras de linha Windows ou espaços extras) em arquivos de configuração.

Por que isso é importante?
Arquivos YAML são extremamente sensíveis à indentação e a caracteres invisíveis.
Se um arquivo foi editado em um editor Windows e enviado para o Linux, ele
pode conter caracteres '\r' ($ no cat -A) que quebram o interpretador da
aplicação, resultando em erros genéricos como "failed to use db type".

Conceitos-chave:
1. cat -A: Mostrar o final das linhas com $ e tabs com ^I.
2. Sanitização de Configuração: Garantir que o arquivo é puro texto Linux.
3. Troubleshooting de Parsers: Resolver erros de leitura de arquivos estruturados.
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

        path = "/var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"
        print(f"Auditando caracteres invisíveis em {path}...")
        # Comando para mostrar caracteres especiais
        cmd = f'sudo -S cat -A "{path}" | head -n 20'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Conteúdo Bruto (Raw) ---")
            print(results)
        else:
            print("Não foi possível ler o arquivo ou ele está vazio.")

        client.close()
    except Exception as e:
        print(f"Erro na auditoria bruta: {e}")


if __name__ == "__main__":
    main()
