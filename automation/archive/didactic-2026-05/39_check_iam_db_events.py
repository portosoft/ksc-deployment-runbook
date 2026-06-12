#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 39: DIAGNÓSTICO DE CONEXÃO DE MICROSERVIÇOS
---------------------------------------------------------
Este script ensina como auditar o relacionamento de um serviço com o seu
banco de dados através da análise de logs focada.

Por que isso é importante?
Microserviços (como o IAM) operam de forma independente. Se eles não conseguem
conectar ao banco de dados, a aplicação simplesmente não funcionará. Buscar
por 'database' nos logs do serviço permite identificar erros de credenciais,
timemouts ou falhas de DNS que impedem o provisionamento correto.

Conceitos-chave:
1. Filtragem por Infraestrutura: Buscar termos como 'database', 'connection' ou 'sql'.
2. Diagnóstico de Serviço Isolado: Não depender do log central do servidor.
3. Auditoria de Conectividade: Garantir que o serviço "fala" com o seu banco.
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

        service = "kliam_srv"
        print(f'Buscando eventos de banco de dados no serviço "{service}"...')

        # Busca no log do serviço por termos relacionados a banco de dados
        cmd_log = f'sudo -S journalctl -u "{service}" --since "24 hours ago" | grep -iE "database|connection|sql" | tail -n 50'
        stdin_log, stdout_log, stderr_log = client.exec_command(cmd_log)
        stdin_log.write(password + "\n")
        stdin_log.flush()

        print(f"--- Eventos de Banco em {service} ---")
        print(stdout_log.read().decode())

        print("Verificando diretório de configuração do IAM...")
        cmd_ls = "ls -F /var/opt/kaspersky/klnagent_srv/iam/"
        stdin_ls, stdout_ls, stderr_ls = client.exec_command(cmd_ls)
        print("--- Conteúdo do Diretório ---")
        print(stdout_ls.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro no diagnóstico de conexão: {e}")


if __name__ == "__main__":
    main()
