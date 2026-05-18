#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 41: TESTE DE COMANDOS DE INICIALIZAÇÃO (VERBOS DE BINÁRIO)
----------------------------------------------------------------------
Este script ensina como testar "verbos" de comando em binários Go para
disparar funções de manutenção ocultas.

Por que isso é importante?
Muitas aplicações modernas usam o mesmo binário para o serviço e para as
ferramentas de manutenção. Ao passar comandos como 'migrate' ou 'init',
podemos forçar a aplicação a rodar os scripts internos de banco de dados
que ela normalmente só rodaria durante uma instalação limpa.

Conceitos-chave:
1. Binary Verbs: Comandos passados após o nome do programa (ex: kliam migrate).
2. Forçar Manutenção: Executar lógicas de setup em um sistema já instalado.
3. Diagnóstico por Tentativa de Execução: Testar comandos baseados nas strings encontradas.
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

        # Tentamos o verbo 'migrate' que é comum em apps Go
        cmd = "sudo -S /opt/kaspersky/ksc64/sbin/kliam migrate --config /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"

        print(f"Tentando comando de migração forçada: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        # Capturamos a saída para ver se ele aceitou o comando
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        print("--- Saída do Comando ---")
        if output:
            print(output)
        if error:
            print(f"ERRO/AVISO: {error}")

        client.close()
    except Exception as e:
        print(f"Erro na tentativa de migração: {e}")


if __name__ == "__main__":
    main()
