#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 29: FORENSE DE BINÁRIO (STRINGS & GREP)
-----------------------------------------------------
Este script ensina como "olhar dentro" de um arquivo binário compilado para
encontrar trechos de texto legíveis, como comandos SQL.

Por que isso é importante?
Muitas aplicações modernas não usam scripts SQL externos por segurança.
Elas embutem o código de criação de tabelas diretamente no executável. Usar
o comando 'strings' permite que o engenheiro veja esses comandos, entendendo
quais tabelas o programa espera encontrar ou criar.

Conceitos-chave:
1. strings: Extrai sequências de caracteres imprimíveis de arquivos binários.
2. Inspecionando Binários: Técnica de engenharia reversa para diagnóstico.
3. Extração de DDL: Encontrar o código de criação de tabelas oculto no binário.
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

        binary_path = "/opt/kaspersky/ksc64/sbin/kliam"
        print(f"Realizando forense no binário {binary_path}...")

        # Busca por comandos CREATE TABLE dentro do binário
        cmd = f'sudo -S strings "{binary_path}" | grep -i "CREATE TABLE" | head -n 20'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Comandos SQL Encontrados no Binário ---")
            print(results)
        else:
            print("Nenhum comando CREATE TABLE encontrado no binário.")

        client.close()
    except Exception as e:
        print(f"Erro na análise forense: {e}")


if __name__ == "__main__":
    main()
