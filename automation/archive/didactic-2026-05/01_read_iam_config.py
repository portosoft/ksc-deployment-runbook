#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 01: LEITURA DE CONFIGURAÇÃO REMOTA VIA SSH
--------------------------------------------------------
Este script ensina como acessar e ler arquivos protegidos (root) em um servidor
Linux remoto usando Python.

Por que isso é importante?
Em ambientes DevSecOps, raramente temos acesso direto aos arquivos de produção.
Automatizar a leitura via SSH permite auditar configurações sem precisar
fazer login manual em cada máquina, mantendo a rastreabilidade.

Conceitos-chave:
1. Paramiko: Biblioteca padrão para comunicações SSH em Python.
2. Escalonamento de Privilégios (sudo -S): Permite executar comandos como root
   enviando a senha de forma programática pelo fluxo de entrada (stdin).
3. Segurança de Segredos: Uso de variáveis de ambiente (.env) para evitar
   vazamento de senhas no código fonte.
"""

import os
import paramiko
from dotenv import load_dotenv

def main():
    # Carregar variáveis de ambiente com aspas de proteção
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print(f"Conectado ao host: {host}")

        path = "/var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"
        cmd = f"sudo -S cat \"{path}\""

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        content = stdout.read().decode()
        if content:
            print(f"--- Conteúdo de {path} ---")
            print(content)
        else:
            print("Erro ou arquivo vazio. Verifique o log de erro.")
            print(stderr.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro na execução: {e}")

if __name__ == "__main__":
    main()
