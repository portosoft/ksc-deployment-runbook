#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 07: COMPARAÇÃO DE LINHA DE BASE (BASELINE)
---------------------------------------------------------
Este script demonstra a técnica de auditoria por comparação entre ambientes.

Por que isso é importante?
Quando um sistema para de funcionar (como o ksciam), a forma mais rápida de
diagnosticar é compará-lo com um sistema que ainda funciona (como o ksc).
Identificar as diferenças de configuração (extensões, permissões, etc)
frequentemente revela a causa raiz do problema.

Conceitos-chave:
1. Baseline Audit: Usar um estado conhecido como "bom" para validar outros.
2. Análise de Discrepâncias: Focar no que é DIFERENTE entre os dois bancos.
3. Troubleshooting de Infraestrutura: Técnica essencial para engenheiros seniores.
"""

import os
import paramiko
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    ref_db = os.getenv("KSC_DB_NAME")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)

        print(f'Consultando extensões no banco de referência ("{ref_db}")...')
        q = "SELECT extname FROM pg_extension;"
        cmd = f'sudo -S -u postgres psql -d "{ref_db}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print(f"--- Extensões no {ref_db} (Referência) ---")
        print(stdout.read().decode().strip())

        client.close()
    except Exception as e:
        print(f"Erro na comparação: {e}")


if __name__ == "__main__":
    main()
