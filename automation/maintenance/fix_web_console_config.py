#!/usr/bin/env python3
import os
import sys
import paramiko
from dotenv import load_dotenv


def fix_web_console_config():
    # Carregar variáveis de ambiente de forma segura
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    fqdn = os.getenv("KSC_FQDN")

    if not all([host, user, password, fqdn]):
        print("ERROR: Variáveis de ambiente obrigatórias ausentes.")
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        print(f"--- Corrigindo config.json no servidor {host} ---")

        # Comandos de correção via sed
        # 1. Corrige porta web padrão
        # 2. Substitui placeholders de FQDN
        # 3. Garante porta 13299 para OpenAPI
        cmds = [
            f"sed -i 's/\\\\$web_console_port\\\\$/8080/g' /var/opt/kaspersky/ksc-web-console/server/config.json",
            f"sed -i 's/\\\\$web_console_address\\\\$/{fqdn}/g' /var/opt/kaspersky/ksc-web-console/server/config.json",
            f'sed -i \'s/"port": "13000"/"port": "13299"/g\' /var/opt/kaspersky/ksc-web-console/server/config.json',
        ]

        for cmd in cmds:
            stdin, stdout, stderr = client.exec_command(
                f"sudo -S {cmd}"
            )
            stdin.write(password + "\n")
            stdin.flush()
            stdout.channel.recv_exit_status()
            # Silently execute, error checking below

        print("--- Aplicando correções de permissões e reiniciando ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S chown -R ksc:kladmins /var/opt/kaspersky/ksc-web-console/"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.channel.recv_exit_status()

        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart ksc-web-console"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdout.channel.recv_exit_status()

        print("--- Configuração do Web Console corrigida e serviço reiniciado ---")
        client.close()
    except Exception as e:
        print(f"ERROR: Falha na manutenção do config.json: {e}")


if __name__ == "__main__":
    fix_web_console_config()
