# -*- coding: utf-8 -*-
"""
Script Operacional para correções no config.json do Kaspersky Web Console.
"""

import logging
from automation.python.config import KscConfig
from automation.python.remote import connect_ksc_host, run_remote_sudo
from automation.python.logging_utils import (
    init_evidence_dir,
    configure_logger,
    log_json,
)
from automation.ops.purge_iam_mfa import OpsError

logger = logging.getLogger(__name__)


def fix_web_console_config(config: KscConfig, apply: bool = False) -> None:
    """
    Aplica correções de portas e hosts via sed no config.json do Web Console.
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

    # Comandos de correção usando sed
    cmds = [
        r"sed -i 's/\\$web_console_port\\$/8080/g' /var/opt/kaspersky/ksc-web-console/server/config.json",
        f"sed -i 's/\\\\$web_console_address\\\\$/{config.ksc_fqdn}/g' /var/opt/kaspersky/ksc-web-console/server/config.json",
        r'sed -i \'s/"port": "13000"/"port": "13299"/g\' /var/opt/kaspersky/ksc-web-console/server/config.json',
    ]

    if not apply:
        run_logger.info(
            "[CHECK] Seriam aplicadas as seguintes correções via sed no config.json remoto:"
        )
        for cmd in cmds:
            run_logger.info(f"  - {cmd}")
        run_logger.info(
            "[CHECK] A propriedade de /var/opt/kaspersky/ksc-web-console/ seria alterada para ksc:kladmins."
        )
        run_logger.info("[CHECK] O serviço ksc-web-console seria reiniciado.")
        log_json(run_logger, "fix_web_config_check_only")
        return

    client = None
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        # Executa comandos de substituição
        for cmd in cmds:
            log_json(run_logger, "run_command_start", cmd=cmd)
            out, err, status = run_remote_sudo(client, cmd, config.ksc_pass)
            log_json(
                run_logger, "run_command_end", status=status, stdout=out, stderr=err
            )

            if status != 0:
                raise OpsError(f"Falha ao executar sed no config.json: {err}")

        # Corrige permissões de dono/grupo
        chown_cmd = "chown -R ksc:kladmins /var/opt/kaspersky/ksc-web-console/"
        log_json(run_logger, "run_command_start", cmd=chown_cmd)
        out, err, status = run_remote_sudo(client, chown_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stdout=out, stderr=err)

        if status != 0:
            raise OpsError(f"Falha ao rodar chown na pasta do web console: {err}")

        # Reinicia o serviço
        restart_cmd = "systemctl restart ksc-web-console"
        log_json(run_logger, "run_command_start", cmd=restart_cmd)
        out, err, status = run_remote_sudo(client, restart_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stdout=out, stderr=err)

        if status != 0:
            raise OpsError(f"Falha ao reiniciar o serviço ksc-web-console: {err}")

        log_json(run_logger, "fix_web_config_success")
        run_logger.info(
            "Configuração do Web Console corrigida e serviço reiniciado com sucesso."
        )
    except Exception as e:
        log_json(run_logger, "fix_web_config_failed", error=str(e))
        raise OpsError(
            f"Falha operacional ao corrigir configuração do Web Console: {e}"
        )
    finally:
        if client:
            client.close()
