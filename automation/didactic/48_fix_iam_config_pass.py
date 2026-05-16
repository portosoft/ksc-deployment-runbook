#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 48: EDIÇÃO REMOTA DE CONFIGURAÇÃO (SED)
-----------------------------------------------------
Este script ensina como realizar a edição segura de um arquivo de configuração
remoto usando o utilitário 'sed'.

Por que isso é importante?
Muitas vezes, a automação de setup (como o postinstall) falha em atualizar todos
os lugares onde uma senha é armazenada. Saber editar arquivos de forma
cirúrgica usando 'sed' permite corrigir esses "pontos cegos" da automação sem
precisar baixar o arquivo, editar e subir novamente, o que é mais rápido e
menos propenso a erros de permissão.

Conceitos-chave:
1. sed -i: Edição "in-place" (direto no arquivo).
2. Substituição de Padrão: Trocar uma string antiga por uma nova.
3. Manutenção de Infraestrutura: Corrigir credenciais dessincronizadas.
"""

import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    new_db_pass = os.getenv("KSC_DB_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        path = "/var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"
        print(f"Atualizando a senha do banco no arquivo {path}...")

        # Comando SED para trocar o valor de dbms_userpassword
        # Usamos o caractere | como delimitador para evitar conflitos com barras na senha
        cmd = f"sudo -S sed -i \"s|dbms_userpassword:.*|dbms_userpassword: \\\"{new_db_pass}\\\"|\" \"{path}\""

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print("Senha atualizada com sucesso.")

        print("Reiniciando serviço kliam_srv para aplicar a nova credencial...")
        client.exec_command("sudo -S systemctl restart kliam_srv")

        client.close()
    except Exception as e:
        print(f"Erro na edição da configuração: {e}")

if __name__ == "__main__":
    main()
