#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 18: INVESTIGAÇÃO DE LOGS DE INSTALAÇÃO TEMPORÁRIOS
---------------------------------------------------------------
Este script ensina como localizar arquivos de log criados durante processos
de instalação ou configuração de software (como o postinstall da Kaspersky).

Por que isso é importante?
Instaladores muitas vezes não usam o sistema de log padrão do SO (syslog/journal)
enquanto estão rodando. Eles criam arquivos temporários no /tmp para registrar
o progresso. Se o seu setup falha, a resposta quase sempre está escondida
em um desses arquivos kl-install-*.log.

Conceitos-chave:
1. Wildcards (Coringa *): Usar padrões de nome para encontrar múltiplos arquivos.
2. Análise de Logs de Setup: Entender o fluxo de execução de um instalador.
3. Troubleshooting de Instalação: O /tmp é o primeiro lugar a olhar em falhas de setup.
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

        print("Procurando logs de instalação no /tmp...")
        # Comando para listar arquivos que seguem o padrão da Kaspersky
        cmd = "ls -t /tmp/kl-install*.log 2>/dev/null | head -n 5"

        stdin, stdout, stderr = client.exec_command(cmd)

        results = stdout.read().decode().strip()
        if results:
            print("--- Logs de Instalação Encontrados (Mais recentes primeiro) ---")
            files = results.split("\n")
            for f in files:
                print(f"Lendo o arquivo: {f}")
                # Lemos as últimas 50 linhas de cada log para ver o erro final
                stdin_log, stdout_log, stderr_log = client.exec_command(f"sudo -S tail -n 50 \"{f}\"")
                stdin_log.write(password + "\n")
                stdin_log.flush()
                print(stdout_log.read().decode())
                print("-" * 40)
        else:
            print("Nenhum log de instalação encontrado no /tmp.")

        client.close()
    except Exception as e:
        print(f"Erro na busca de logs: {e}")

if __name__ == "__main__":
    main()
