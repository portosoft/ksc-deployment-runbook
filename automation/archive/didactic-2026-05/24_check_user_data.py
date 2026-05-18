#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 24: VERIFICAÇÃO DE POPULAMENTO DE DADOS
-----------------------------------------------------
Este script ensina como auditar se as tabelas do banco de dados contêm dados
reais após uma reconstrução estrutural.

Por que isso é importante?
Ter as tabelas (a "casca") é apenas metade da solução. Sem os dados (o "miolo"),
como os registros de usuários e permissões, o sistema continuará falhando
no login. Validar o populamento ajuda a decidir se precisamos forçar uma
sincronização ou se o sistema já se recuperou sozinho.

Conceitos-chave:
1. Data Integrity: Garantir que as informações de negócio foram migradas/criadas.
2. COUNT(*): Usado aqui para validar a presença de registros de identidade.
3. Auditoria de Conteúdo: O passo final após validar a estrutura do banco.
"""

import os
import paramiko
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    db_name = os.getenv("KSC_IAM_NAME")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        print("Verificando populamento de usuários no esquema 'iam'...")
        # Consulta para contar registros na tabela de usuários (identidades)
        # Nota: Usamos aspas duplas no nome do esquema e tabela para segurança
        q = "SELECT COUNT(*) FROM iam.users;"
        cmd = f'sudo -S -u postgres psql -d "{db_name}" -t -c "{q}"'

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        result = stdout.read().decode().strip()
        print(f"Total de usuários encontrados no banco IAM: {result}")

        client.close()
    except Exception as e:
        print(f"Erro na verificação de dados: {e}")


if __name__ == "__main__":
    main()
