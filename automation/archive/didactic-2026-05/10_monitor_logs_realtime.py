#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 10: MONITORAMENTO DE LOGS EM TEMPO REAL
------------------------------------------------------
Este script ensina como monitorar continuamente um arquivo de log remoto
enquanto o sistema opera.

Por que isso é importante?
Muitas vezes precisamos ver o que acontece no sistema no exato momento em
que executamos uma ação (como reiniciar um serviço). O monitoramento
persistente (tail -f) captura mensagens que podem sumir rapidamente ou
não serem persistidas em caso de queda do servidor.

Conceitos-chave:
1. Tail Persistente (tail -f): Acompanhar o fluxo de escrita do arquivo.
2. SSH Channel: Abrir uma sessão de dados dedicada para o log.
3. Monitoramento de "Causa e Efeito": Técnica vital para diagnóstico de falhas.
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

        log_path = "/var/log/kaspersky/ak_server.log"
        print(f'Monitorando "{log_path}" por 30 segundos...')

        # Abrir uma sessão SSH dedicada (canal) para o comando contínuo
        transport = client.get_transport()
        channel = transport.open_session()
        channel.exec_command(f'sudo -S tail -f "{log_path}"')

        # Enviar senha do sudo
        channel.send(password + "\n")

        start_time = time.time()
        while time.time() - start_time < 30:  # Monitorar por 30s
            if channel.recv_ready():
                print(channel.recv(1024).decode(), end="")
            time.sleep(1)

        channel.close()
        client.close()
    except Exception as e:
        print(f"Erro no monitoramento: {e}")


if __name__ == "__main__":
    main()
