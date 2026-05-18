#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 22: MONITORAMENTO DE REINÍCIO DE SERVIÇO (RESTART & TAIL)
----------------------------------------------------------------------
Este script ensina como capturar o comportamento crítico de uma aplicação
durante o seu "nascimento" (reinício do serviço).

Por que isso é importante?
A maioria das aplicações realiza checagens de banco de dados e migrações
apenas durante a inicialização. Se o serviço já está rodando, ele não tentará
criar novas tabelas. Reiniciar o serviço enquanto monitoramos os logs é a
forma mais eficaz de ver por que uma migração não está ocorrendo.

Conceitos-chave:
1. systemctl restart: Forçar o recarregamento completo da aplicação.
2. Captura de Boot-up: Observar mensagens de inicialização e erro de conexão.
3. Diagnóstico de Estado Inicial: Verificar se a aplicação detecta o banco vazio.
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
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        service = "kliam_srv"
        print(f'Reiniciando o serviço "{service}" e capturando logs iniciais...')

        # Executa o restart
        cmd_restart = f'sudo -S systemctl restart "{service}"'
        stdin, stdout, stderr = client.exec_command(cmd_restart)
        stdin.write(password + "\n")
        stdin.flush()

        # Aguarda um pequeno intervalo para o serviço começar a logar
        time.sleep(3)

        # Captura os logs mais recentes (últimas 30 linhas) do Journal
        cmd_logs = f'sudo -S journalctl -u "{service}" -n 30 --no-pager'
        stdin_l, stdout_l, stderr_l = client.exec_command(cmd_logs)
        stdin_l.write(password + "\n")
        stdin_l.flush()

        results = stdout_l.read().decode().strip()
        if results:
            clean_text = "".join(c for c in results if ord(c) < 128)
            print("--- Logs de Inicialização ---")
            print(clean_text)
        else:
            print("Nenhum log capturado após o reinício.")

        client.close()
    except Exception as e:
        print(f"Erro no reinício/monitoramento: {e}")


if __name__ == "__main__":
    main()
