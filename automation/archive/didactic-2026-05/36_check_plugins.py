#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 36: AUDITORIA DE PLUGINS DE SERVIDOR
--------------------------------------------------
Este script ensina como verificar quais extensões (plugins) estão ativas
em um serviço complexo como o Kaspersky Security Center.

Por que isso é importante?
O KSC é modular. Se o plugin responsável pela gestão de identidades (IAM)
não for carregado durante o boot do servidor, as tabelas nunca serão
provisionadas e o login falhará. Validar os plugins ativos é essencial para
garantir que o software está "completo" em memória.

Conceitos-chave:
1. Plugins de Servidor: Módulos que adicionam funcionalidades ao binário principal.
2. Inspecionando o Estado em Execução: Ver o que o servidor carregou.
3. Troubleshooting de Modularidade: Identificar se algum componente vital falhou.
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

        print("Consultando plugins carregados no klserver...")
        # Comando para listar plugins ativos (pode variar conforme a versão)
        cmd = "sudo -S /opt/kaspersky/ksc64/sbin/klserver -plugins 2>&1 | head -n 50"

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Plugins Detectados ---")
            print(results)
        else:
            print("Nenhum plugin listado ou erro na execução do comando.")

        client.close()
    except Exception as e:
        print(f"Erro na auditoria de plugins: {e}")


if __name__ == "__main__":
    main()
