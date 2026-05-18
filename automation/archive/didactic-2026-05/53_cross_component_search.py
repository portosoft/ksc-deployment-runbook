#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 53: BUSCA TRANSVERSAL DE COMPONENTES (GREP & STRINGS)
------------------------------------------------------------------
Este script ensina como realizar buscas coordenadas em arquivos de
script (.pm) e binários (.sbin) para mapear a arquitetura da aplicação.

Por que isso é importante?
Em sistemas complexos, a funcionalidade é dividida. O 'klsrvconfig' pode mudar
a senha, mas o 'appdata.pm' pode ser quem cria as tabelas. Realizar uma
busca transversal permite que você conecte os pontos, entendendo o fluxo
completo de como a aplicação gerencia o componente de identidade (IAM).

Conceitos-chave:
1. Multi-file Grepping: Buscar em vários arquivos de tipos diferentes.
2. Mapeamento de Fluxo: Identificar quem chama quem no sistema.
3. Troubleshooting Holístico: Olhar para o sistema como um todo, não apenas um arquivo.
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

        print("Buscando 'iam' no módulo appdata.pm...")
        cmd_pm = 'sudo -S grep -i "iam" /opt/kaspersky/ksc64/lib/bin/setup/appdata.pm'
        stdin_p, stdout_p, stderr_p = client.exec_command(cmd_pm)
        stdin_p.write(password + "\n")
        stdin_p.flush()
        print("--- Resultados em appdata.pm ---")
        print(stdout_p.read().decode())

        print("\nBuscando 'iam' no binário klsrvconfig...")
        cmd_bin = (
            'sudo -S strings /opt/kaspersky/ksc64/sbin/klsrvconfig | grep -i "iam"'
        )
        stdin_b, stdout_b, stderr_b = client.exec_command(cmd_bin)
        stdin_b.write(password + "\n")
        stdin_b.flush()
        print("--- Resultados em klsrvconfig ---")
        print(stdout_b.read().decode())

        client.close()
    except Exception as e:
        print(f"Erro na busca transversal: {e}")


if __name__ == "__main__":
    main()
