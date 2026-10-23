# -*- coding: utf-8 -*-
"""
Script Operacional para correções no config.json do Kaspersky Web Console via JSON nativo.
"""

import json
import logging
import tempfile
import uuid
from pathlib import Path

from automation.ops.purge_iam_mfa import OpsError
from automation.python.config import KscConfig
from automation.python.logging_utils import (
    configure_logger,
    init_evidence_dir,
    log_json,
)
from automation.python.remote import connect_ksc_host, run_remote_sudo
from automation.python.utils.secure_file import write_secure_file

logger = logging.getLogger(__name__)

REMOTE_CONFIG_PATH = "/var/opt/kaspersky/ksc-web-console/server/config.json"


def fix_web_console_config(config: KscConfig, apply: bool = False) -> None:
    """
    Aplica correções de portas e hosts via JSON nativo no config.json do Web Console.
    Se apply for False, apenas simula (--check).
    """
    evidence_dir = init_evidence_dir("fix_web_config")
    run_logger = configure_logger(evidence_dir)
    log_json(
        run_logger,
        "fix_web_config_start",
        host=config.ksc_host,
        user=config.ksc_user,
        apply=apply,
    )

    if not apply:
        run_logger.info(
            f"[CHECK] Seria lido e atualizado via JSON nativo o arquivo {REMOTE_CONFIG_PATH}:"
        )
        run_logger.info(f"  - port: {config.web_port}")
        run_logger.info(f"  - address: {config.ksc_fqdn}")
        run_logger.info("  - openAPIServers[*].port: 13299")
        run_logger.info(
            "[CHECK] A propriedade de /var/opt/kaspersky/ksc-web-console/ seria alterada para ksc:kladmins."
        )
        run_logger.info("[CHECK] O serviço ksc-web-console seria reiniciado.")
        log_json(
            run_logger,
            "fix_web_config_check_only",
            port=config.web_port,
            fqdn=config.ksc_fqdn,
        )
        return

    client = None
    remote_tmp_dir = None
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        # 1. Leitura remota do config.json
        cat_cmd = f"cat {REMOTE_CONFIG_PATH}"
        log_json(run_logger, "run_command_start", cmd=cat_cmd)
        out, err, status = run_remote_sudo(client, cat_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stderr=err)

        if status != 0:
            raise OpsError(f"Falha ao ler {REMOTE_CONFIG_PATH}: {err}")

        # 2. Parsing de JSON nativo
        try:
            data = json.loads(out)
        except Exception as e:
            raise OpsError(f"Falha ao interpretar JSON do config.json: {e}")

        # 3. Ajuste de campos dinâmicos
        data["port"] = config.web_port
        data["address"] = config.ksc_fqdn
        if "openAPIServers" in data and isinstance(data["openAPIServers"], list):
            for srv in data["openAPIServers"]:
                if isinstance(srv, dict):
                    srv["port"] = "13299"

        json_content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

        # 4. Gravação atômica local com write_secure_file e transferência segura
        with tempfile.TemporaryDirectory() as tmp_local_dir:
            local_file = Path(tmp_local_dir) / "config.json"
            write_secure_file(str(local_file), json_content, mode=0o600)

            # Upload via SFTP para diretório temporário restrito no host remoto
            remote_tmp_dir = f"/tmp/ksc_web_cfg_{uuid.uuid4().hex}"
            remote_tmp_file = f"{remote_tmp_dir}/config.json"

            sftp = client.open_sftp()
            sftp.mkdir(remote_tmp_dir, mode=0o700)
            f = sftp.file(remote_tmp_file, "w")
            f.chmod(0o600)
            f.write(json_content)
            f.close()
            sftp.close()

            # Substituição atômica via sudo no destino final
            mv_cmd = f"cp '{remote_tmp_file}' '{REMOTE_CONFIG_PATH}'"
            log_json(run_logger, "run_command_start", cmd=f"cp ... {REMOTE_CONFIG_PATH}")
            out, err, status = run_remote_sudo(client, mv_cmd, config.ksc_pass)
            log_json(run_logger, "run_command_end", status=status, stderr=err)
            if status != 0:
                raise OpsError(f"Falha ao aplicar config.json no destino: {err}")

        # 5. Ajuste de permissões de dono e grupo
        chown_cmd = "chown -R ksc:kladmins /var/opt/kaspersky/ksc-web-console/"
        log_json(run_logger, "run_command_start", cmd=chown_cmd)
        out, err, status = run_remote_sudo(client, chown_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stderr=err)
        if status != 0:
            raise OpsError(f"Falha ao rodar chown na pasta do web console: {err}")

        # 6. Reinicia o serviço
        restart_cmd = "systemctl restart ksc-web-console"
        log_json(run_logger, "run_command_start", cmd=restart_cmd)
        out, err, status = run_remote_sudo(client, restart_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stderr=err)
        if status != 0:
            raise OpsError(f"Falha ao reiniciar o serviço ksc-web-console: {err}")

        log_json(run_logger, "fix_web_config_success")
        run_logger.info(
            "Configuração do Web Console corrigida via JSON nativo e serviço reiniciado com sucesso."
        )

    except Exception as e:
        log_json(run_logger, "fix_web_config_failed", error=str(e))
        raise OpsError(f"Falha operacional ao corrigir configuração do Web Console: {e}")
    finally:
        if client:
            if remote_tmp_dir:
                try:
                    run_remote_sudo(
                        client,
                        f"rm -rf '{remote_tmp_dir}'",
                        config.ksc_pass,
                    )
                except Exception:
                    pass
            client.close()
