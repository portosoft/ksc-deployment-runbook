#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 21: ANÁLISE DE LOGS DE MICROSERVIÇOS (JOURNALCTL -U)
------------------------------------------------------------------
Este script ensina como isolar a auditoria em um único microserviço do sistema
usando o comando journalctl com o filtro de unidade (-u).

Por que isso é importante?
Arquiteturas modernas (como a do KSC 16.2) usam múltiplos serviços independentes.
O 'kliam_srv' é o responsável exclusivo pela identidade. Se houver um erro no
banco ksciam, este erro raramente aparecerá no log geral do servidor, mas
estará detalhado aqui.

Conceitos-chave:
1. Isolação de Componente: Focar no log de quem realmente "fala" com o banco.
2. Análise Temporal: Ver o que mudou na última hora de operação.
3. Microserviços: Diagnosticar falhas em sistemas distribuídos.
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

        service = "kliam_srv"
        print(f'Consultando logs do microserviço "{service}"...')

        # Consulta logs do serviço na última hora
        cmd = f'sudo -S journalctl -u "{service}" --since "1 hour ago" --no-pager | tail -n 50'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        results = stdout.read().decode().strip()
        if results:
            # Limpeza básica para o console Windows (ASCII)
            clean_text = "".join(c for c in results if ord(c) < 128)
            print(f"--- Logs de {service} ---")
            print(clean_text)
        else:
            print(f'Nenhum log encontrado para o serviço "{service}" na última hora.')

        client.close()
    except Exception as e:
        print(f"Erro na auditoria do microserviço: {e}")


if __name__ == "__main__":
    main()
