#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 19: TRATAMENTO DE CODIFICAÇÃO E STATUS DE SERVIÇO
---------------------------------------------------------------
Este script ensina como capturar o estado de um serviço Linux e lidar com
problemas de codificação (UTF-8 vs CP1252/Windows).

Por que isso é importante?
Comandos Linux como 'systemctl status' usam caracteres especiais (como pontos
coloridos ou setas) que o Windows muitas vezes não consegue exibir, causando
erros de execução no seu script Python. Tratar a codificação garante que
sua automação seja robusta e cross-platform.

ATUALIZAÇÃO: FILTRAGEM DE CARACTERES (WINDOWS)
----------------------------------------------
Para evitar o erro "UnicodeEncodeError" no console do Windows, adicionamos
uma lógica de filtragem que mantém apenas caracteres ASCII básicos. Isso
garante que o script não "quebre" ao tentar imprimir símbolos de status do Linux.

Conceitos-chave:
1. systemctl status: Verificar se um serviço está rodando, parado ou falhou.
2. UTF-8 Decoding: Converter os bytes do Linux para texto legível.
3. Robustez Cross-Platform: Garantir que o script rode bem em Windows e Linux.
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

        print("Verificando estado do kladminserver_srv...")
        cmd = "systemctl status kladminserver_srv --no-pager"

        stdin, stdout, stderr = client.exec_command(cmd)

        output_bytes = stdout.read()
        output_text = output_bytes.decode("utf-8", "replace")

        # FILTRO DE COMPATIBILIDADE:
        # Remove caracteres que causariam erro de codec no print do Windows
        clean_text = "".join(c for c in output_text if ord(c) < 128)

        print("--- Status do Servidor (Processado para Windows) ---")
        print(clean_text)

        client.close()
    except Exception as e:
        print(f"Erro ao verificar status: {e}")


if __name__ == "__main__":
    main()
