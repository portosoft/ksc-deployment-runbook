#!/usr/bin/env python3
import os
import sys

"""
Script para converter arquivo .env em variáveis YAML para o Ansible.
Lê '.env' na raiz e gera 'automation/ansible/group_vars/generated_from_env.yml'.
"""


def main():
    env_path = os.path.join(os.getcwd(), ".env")
    output_dir = os.path.join(os.getcwd(), "automation", "ansible", "group_vars")
    output_file = os.path.join(output_dir, "generated_from_env.yml")

    if not os.path.exists(env_path):
        print(f"Erro: Arquivo .env não encontrado em {env_path}")
        print("Crie um arquivo .env baseado no example antes de rodar este script.")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(env_path, "r") as env_file:
            lines = env_file.readlines()

        yaml_vars = [
            "---",
            "# Gerado automaticamente a partir do .env",
            "# NÃO EDITE ESTE ARQUIVO DIRETAMENTE",
        ]

        for line in lines:
            line = line.strip()
            # Ignorar comentários e linhas em branco
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                # Converter chave para minúscula conforme pedido
                yaml_key = key.strip().lower()
                yaml_value = value.strip().strip('"').strip("'")
                yaml_vars.append(f'{yaml_key}: "{yaml_value}"')

        # Ensure the output file is created with secure permissions (0o600)
        fd = os.open(output_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as out:
            out.write("\n".join(yaml_vars) + "\n")

        print(f"Sucesso! Variáveis convertidas para: {output_file}")

    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
