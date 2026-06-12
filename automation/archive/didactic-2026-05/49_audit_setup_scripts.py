#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 49: AUDITORIA DE SCRIPTS DE SETUP INTERNOS
---------------------------------------------------------
Este script ensina como explorar os bastidores da instalação de um software,
mapeando scripts que não são disparados pelo assistente principal.

Por que isso é importante?
Grandes softwares (como o KSC) são compostos por dezenas de pequenos scripts de
setup. Se o assistente principal (postinstall.pl) falhar em disparar um desses
scripts, a instalação ficará incompleta. Saber localizar e testar esses scripts
individuais é a chave para resolver "instalações parciais".

Conceitos-chave:
1. Setup Binaries: Pequenos programas usados apenas durante a instalação.
2. Auditoria de Fluxo de Instalação: Entender a sequência de comandos do software.
3. Descoberta de Gatilhos: Encontrar scripts como 'setup_iam.sh' ou similares.
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

        setup_path = "/opt/kaspersky/ksc64/lib/bin/setup/"
        print(f"Listando scripts de setup em {setup_path}...")

        # Lista arquivos executáveis no diretório de setup
        cmd = f"ls -F {setup_path}"

        stdin, stdout, stderr = client.exec_command(cmd)

        results = stdout.read().decode().strip()
        if results:
            print("--- Componentes de Setup Encontrados ---")
            print(results)
        else:
            print("Nenhum componente de setup encontrado no diretório.")

        client.close()
    except Exception as e:
        print(f"Erro na auditoria de setup: {e}")


if __name__ == "__main__":
    main()
