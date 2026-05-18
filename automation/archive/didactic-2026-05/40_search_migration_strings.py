#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 40: ENGENHARIA REVERSA DE COMANDOS DE MIGRAÇÃO
------------------------------------------------------------
Este script ensina como localizar referências a mecanismos de migração
interna dentro de um binário compilado.

Por que isso é importante?
Aplicações modernas muitas vezes ocultam seus comandos de manutenção. Ao buscar
por 'migration' no binário, podemos descobrir flags como '-migrate',
'-setup-db' ou caminhos de arquivos de controle que nos permitem forçar a
criação das tabelas que estão faltando.

Conceitos-chave:
1. Migration Discovery: Encontrar o sistema de versionamento interno.
2. Análise de Strings Técnicas: Identificar o "motor" de banco de dados da aplicação.
3. Troubleshooting Proativo: Antecipar como a aplicação evolui seu esquema.
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

        binary_path = "/opt/kaspersky/ksc64/sbin/kliam"
        print(f"Buscando comandos de migração no binário {binary_path}...")

        # Busca por termos relacionados a migração
        cmd = f'sudo -S strings "{binary_path}" | grep -i "migration" | tail -n 20'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            print("--- Termos de Migração Encontrados ---")
            print(results)
        else:
            print("Nenhum termo de migração encontrado no binário.")

        client.close()
    except Exception as e:
        print(f"Erro na busca de migração: {e}")


if __name__ == "__main__":
    main()
