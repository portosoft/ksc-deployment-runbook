#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 17: AUTOMAÇÃO DE REPARO (POSTINSTALL) - VERSÃO SEGURA
-------------------------------------------------------------------
Este script automatiza o assistente de configuração do KSC (postinstall.pl)
usando injeção de respostas via STDIN.

Por que isso é importante?
Assistentes interativos são comuns em software legado ou de infraestrutura.
Saber automatizá-los de forma SEGURA é um diferencial para qualquer engenheiro
DevSecOps. Nesta versão, corrigimos a falha de segurança anterior, garantindo
que nenhuma informação sensível esteja escrita no código.

Segurança (Hardening):
1. Sem Senhas no Código: As credenciais são lidas do arquivo .env.
2. Sem FQDN Exposto: O endereço do servidor é tratado como um segredo.
3. Aspas Duplas: Proteção contra interpretação de caracteres especiais.
"""

import os
import paramiko
from dotenv import load_dotenv


def main():
    # Carregar variáveis de ambiente sanitizadas
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    # Credenciais específicas para o Wizard (Lidas do .env)
    db_pass = os.getenv("KSC_DB_PASS")
    fqdn = os.getenv("KSC_FQDN")
    db_name = os.getenv("KSC_DB_NAME")
    iam_db = os.getenv("KSC_IAM_NAME")
    db_user = os.getenv("KSC_DB_USER")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)

        print("Iniciando a reconfiguração automatizada (Modo Seguro)...")

        # Sequência de respostas para o assistente Kaspersky
        answers = [
            "1",  # Tipo de Banco (1 = Postgres)
            "127.0.0.1",  # Endereço do Banco
            "5432",  # Porta do Banco
            db_name,  # Nome do Banco KSC
            iam_db,  # Nome do Banco IAM
            db_user,  # Usuário do Banco
            db_pass,  # Senha do Banco
            fqdn,  # Endereço FQDN do Servidor
            "ksc",  # Usuário do Serviço
            "kladmins",  # Grupo do Serviço
        ]

        input_data = "\n".join(answers) + "\n"

        cmd = "sudo -S LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl"

        stdin, stdout, stderr = client.exec_command(cmd)

        # Enviar senha do sudo para permissão de execução
        stdin.write(password + "\n")
        stdin.flush()

        # Injetar a sequência de respostas no assistente
        print("Injetando parâmetros de configuração...")
        stdin.write(input_data)
        stdin.flush()

        print("Aguardando provisionamento do banco de dados (2-3 minutos)...")

        # Captura o resultado da execução
        output = stdout.read().decode()
        print("--- Resultado da Operação ---")
        print(output)

        client.close()
    except Exception as e:
        print(f"Erro na automação segura: {e}")


if __name__ == "__main__":
    main()
