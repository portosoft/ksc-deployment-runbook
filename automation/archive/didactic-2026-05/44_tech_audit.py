#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 44: LISTAGEM RECURSIVA E FILTRO TECNOLÓGICO
---------------------------------------------------------
Este script ensina como realizar uma auditoria completa de arquivos e buscar
por tecnologias específicas (Postgres/MySQL) dentro de um binário.

Por que isso é importante?
Quando um erro diz "failed to use db type", ele está reclamando de uma peça
fundamental da infraestrutura. Ao listar todos os arquivos de configuração
recursivamente e buscar por nomes de bancos de dados no binário, podemos
identificar qual palavra exata (PostgreSQL, postgres, pg) o programa espera
receber para funcionar.

Conceitos-chave:
1. ls -laR: Listagem detalhada e recursiva de todos os arquivos, inclusive ocultos.
2. Filtro Tecnológico: Buscar por nomes de softwares específicos (Postgres).
3. Auditoria de Configuração: Mapear todos os arquivos que podem influenciar o serviço.
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

        print("Mapeando arquivos de configuração do IAM (Recursivo)...")
        cmd_ls = "sudo -S ls -laR /var/opt/kaspersky/klnagent_srv/1093/iam/ 2>/dev/null"
        stdin_l, stdout_l, stderr_l = client.exec_command(cmd_ls)
        stdin_l.write(password + "\n")
        stdin_l.flush()
        print("--- Estrutura de Arquivos ---")
        print(stdout_l.read().decode())

        print("\nBuscando termos de banco de dados no binário kliam...")
        cmd_str = "sudo -S strings /opt/kaspersky/ksc64/sbin/kliam | grep -iE \"postgres|mysql|dbtype|db-type\" | head -n 20"
        stdin_s, stdout_s, stderr_s = client.exec_command(cmd_str)
        stdin_s.write(password + "\n")
        stdin_s.flush()
        print("--- Termos de Banco Encontrados ---")
        print(stdout_s.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro na auditoria tecnológica: {e}")

if __name__ == "__main__":
    main()
