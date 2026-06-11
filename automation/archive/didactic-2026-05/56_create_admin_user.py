#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 56: CRIAÇÃO MANUAL DE IDENTIDADE (KLADDUSER)
-----------------------------------------------------------
Este script ensina como usar o utilitário 'kladduser' da Kaspersky para
provisionar usuários administrativos manualmente.

Por que isso é importante?
Quando o provisionamento automático falha (como no nosso caso pós-corrupção),
precisamos de uma forma de "forçar" a entrada de um administrador no sistema.
O 'kladduser' comunica-se com os serviços internos do KSC para criar a
identidade, gerar os hashes de senha corretos e atribuir as funções (roles)
necessárias para o login no Web Console.

Conceitos-chave:
1. kladduser: Utilitário oficial para gestão de usuários via linha de comando.
2. Role Assignment: Atribuir a função de 'Administrator' para controle total.
3. Reparo de Identidade: Restaurar o acesso administrativo em bancos vazios.
"""

import os
import paramiko
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    admin_name = os.getenv("KSC_ADMIN_NAME")
    admin_pass = os.getenv("KSC_ADMIN_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)

        print(f"Criando usuário administrativo '{admin_name}' via kladduser...")
        # Comando para criar o usuário e atribuir o papel de administrador
        # Nota: Usamos o binário kladduser com os parâmetros de nome, senha e função
        cmd = f'sudo -S /opt/kaspersky/ksc64/sbin/kladduser -user "{admin_name}" -pass "{admin_pass}" -role Administrator'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        # O kladduser pode não retornar nada em caso de sucesso
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        print("--- Resultado do kladduser ---")
        if output:
            print(output)
        if "successfully" in error or not error:
            print(f"Usuário '{admin_name}' processado com sucesso.")
        else:
            print(f"Aviso/Erro: {error}")

        client.close()
    except Exception as e:
        print(f"Erro na criação do usuário: {e}")


if __name__ == "__main__":
    main()
