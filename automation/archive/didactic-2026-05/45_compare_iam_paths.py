#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 45: COMPARAÇÃO DE CAMINHOS E LINKS SIMBÓLICOS
------------------------------------------------------------
Este script ensina como auditar dois diretórios que parecem ter a mesma
função no sistema, identificando qual deles é o "oficial".

Por que isso é importante?
Sistemas complexos costumam usar links simbólicos ou diretórios numerados
(como o '1093' do KSC) para gerenciar versões ou instâncias. Se você edita a
configuração no lugar errado, a aplicação nunca verá as mudanças. Comparar
as datas de modificação e o conteúdo revela qual caminho o serviço
realmente utiliza.

Conceitos-chave:
1. Directory Comparison: Validar se dois caminhos são idênticos ou complementares.
2. Naming Conventions: Entender por que existem pastas numeradas no Linux.
3. Troubleshooting de Caminhos: Garantir que a automação aponte para o local correto.
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

        paths = [
            "/var/opt/kaspersky/klnagent_srv/iam/",
            "/var/opt/kaspersky/klnagent_srv/1093/iam/",
        ]

        print("Comparando caminhos de configuração IAM...")
        for p in paths:
            print(f"\n--- Detalhes de {p} ---")
            cmd = f'sudo -S ls -la "{p}"'
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            print(stdout.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro na comparação de caminhos: {e}")


if __name__ == "__main__":
    main()
