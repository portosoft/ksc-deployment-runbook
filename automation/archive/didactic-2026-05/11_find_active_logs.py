#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 11: LOCALIZAÇÃO DINÂMICA DE LOGS ATIVOS
-----------------------------------------------------
Este script ensina como encontrar arquivos que estão sendo modificados no
momento, uma técnica de "rastreio de calor" no sistema.

Por que isso é importante?
Em sistemas complexos, os logs podem ser espalhados por dezenas de pastas.
Procurar arquivos modificados nos últimos minutos (mmin) revela exatamente
onde a atividade está ocorrendo, poupando tempo precioso no diagnóstico.

Conceitos-chave:
1. find -mmin: Comando Linux para localizar arquivos baseados no tempo de modificação.
2. Auditoria de Escrita: Ver para onde o sistema está enviando dados agora.
3. Troubleshooting de Fluxo: Isolar arquivos relevantes em diretórios densos.
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

        print("Procurando logs modificados nos últimos 10 minutos...")
        # Localiza arquivos modificados recentemente na pasta da Kaspersky
        cmd = "sudo -S find /var/log/kaspersky/ -type f -mmin -10"

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Arquivos Ativos Encontrados ---")
            print(results)
        else:
            print("Nenhum arquivo de log foi modificado recentemente.")

        client.close()
    except Exception as e:
        print(f"Erro na busca de logs: {e}")


if __name__ == "__main__":
    main()
