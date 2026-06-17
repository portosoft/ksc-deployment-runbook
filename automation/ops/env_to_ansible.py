# -*- coding: utf-8 -*-
"""
Script Operacional para converter arquivos de configuração .env para variáveis do Ansible.
"""

import os
import logging
import yaml
from automation.python.config import KscConfig
from automation.python.utils.secure_file import write_secure_file
from automation.ops.purge_iam_mfa import OpsError

logger = logging.getLogger(__name__)


def env_to_ansible(
    config: KscConfig, env_path: str = "configs/env/ksc_vars.env", apply: bool = False
) -> None:
    """
    Lê o .env e gera as variáveis do Ansible em 'automation/ansible/group_vars/generated_from_env.yml'.
    Se apply for False, apenas simula (--check).
    """
    output_dir = os.path.join(os.getcwd(), "automation", "ansible", "group_vars")
    output_file = os.path.join(output_dir, "generated_from_env.yml")

    if not os.path.exists(env_path):
        raise OpsError(
            f"Arquivo de configuração de ambiente não encontrado em {env_path}"
        )

    if not apply:
        logger.info(f"[CHECK] O arquivo de ambiente em '{env_path}' seria lido.")
        logger.info(
            f"[CHECK] Seria gerado o arquivo YAML em '{output_file}' com permissões restritas (0600)."
        )
        return

    if not os.path.exists(output_dir):
        # 🛡️ Sentinel: Garante permissões estritas no diretório que conterá segredos
        os.makedirs(output_dir, mode=0o700)

    try:
        with open(env_path, "r", encoding="utf-8") as env_file:
            lines = env_file.readlines()

        header = [
            "---",
            "# Gerado automaticamente a partir do .env",
            "# NÃO EDITE ESTE ARQUIVO DIRETAMENTE",
        ]

        parsed_vars = {}
        for line in lines:
            line = line.strip()
            # Ignora comentários e linhas em branco
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                yaml_key = key.strip().lower()
                yaml_value = value.strip().strip('"').strip("'")
                parsed_vars[yaml_key] = yaml_value

        yaml_content = "\n".join(header) + "\n" + yaml.safe_dump(parsed_vars, default_flow_style=False)

        # 🛡️ Sentinel: Grava o arquivo YAML gerado com permissões restritas 0600
        write_secure_file(output_file, yaml_content, 0o600)
        logger.info(f"Sucesso! Variáveis convertidas para Ansible em: {output_file}")
    except Exception as e:
        raise OpsError(f"Falha ao gerar arquivo de variáveis do Ansible: {e}")


si_name = "env_to_ansible"
