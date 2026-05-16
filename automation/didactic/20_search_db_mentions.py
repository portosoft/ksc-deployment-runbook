#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 20: BUSCA DE PADRÕES (GREP) EM LOGS DE PRODUÇÃO
-------------------------------------------------------------
Este script ensina como filtrar arquivos de log volumosos para encontrar
mensagens específicas relacionadas a um componente (neste caso, o banco 'ksciam').

Por que isso é importante?
Servidores de produção geram milhares de linhas de log por minuto. Tentar
ler tudo manualmente é impossível. O uso de filtros (grep) permite que o
engenheiro vá direto ao ponto, localizando exatamente onde a falha de
conexão ou de provisionamento ocorreu.

Conceitos-chave:
1. grep -i: Busca por padrões ignorando letras maiúsculas/minúsculas.
2. Filtragem de Log: Reduzir o ruído para focar na causa raiz.
3. Diagnóstico de Conexão: Verificar se o servidor está conversando com o banco.
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

        target = "ksciam"
        log_path = "/var/log/kaspersky/ak_server.log"

        print(f"Buscando por menções a \"{target}\" no log do servidor...")
        # Comando para buscar o padrão ignorando case e mostrando as últimas 20 ocorrências
        cmd = f"sudo -S grep -i \"{target}\" \"{log_path}\" | tail -n 20"

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print(f"--- Ocorrências de \"{target}\" Encontradas ---")
            print(results)
        else:
            print(f"Nenhuma menção recente a \"{target}\" encontrada no log.")

        client.close()
    except Exception as e:
        print(f"Erro na busca de logs: {e}")

if __name__ == "__main__":
    main()
