# -*- coding: utf-8 -*-
"""
Script Operacional para reconfiguração/redefinição do usuário kscadmin do KSC.
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


def fix_ksc_auth(config: KscConfig, apply: bool = False) -> None:
    """
    Executa o utilitário kladduser remotamente usando stdin seguro.
    Se apply for False, apenas simula (--check).
    """
    evidence_dir = init_evidence_dir("fix_auth")
    run_logger = configure_logger(evidence_dir)
    log_json(
        run_logger,
        "fix_auth_start",
        host=config.ksc_host,
        user=config.ksc_user,
        apply=apply,
    )

    cmd = (
        "LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib "
        f"/opt/kaspersky/ksc64/sbin/kladduser -n {config.ksc_admin_user} -u {config.ksc_admin_user} -r Administrator"
    )

    if not apply:
        run_logger.info(
            f"[CHECK] Seria executado o utilitário kladduser remoto para o usuário '{config.ksc_admin_user}'."
        )
        run_logger.info(
            "[CHECK] A senha administrativa seria fornecida via fluxo stdin seguro."
        )
        log_json(run_logger, "fix_auth_check_only")
        return

    client = None
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        # Fornece a nova senha de administrador duas vezes via stdin prompt do kladduser
        run_logger.info(
            f"Executando redefinição do usuário administrativo '{config.ksc_admin_user}'..."
        )
        log_json(
            run_logger,
            "run_command_start",
            cmd=f"kladduser -n {config.ksc_admin_user} (secure stdin)",
        )

        inputs = [config.ksc_admin_password, config.ksc_admin_password]
        out, err, status = run_remote_sudo(
            client, cmd, config.ksc_pass, stdin_inputs=inputs
        )

        log_json(run_logger, "run_command_end", status=status, stdout=out, stderr=err)

        if status != 0:
            raise OpsError(
                f"O utilitário kladduser remoto falhou com código {status}: {err}"
            )

        log_json(run_logger, "fix_auth_success")
        run_logger.info(
            f"Usuário administrativo '{config.ksc_admin_user}' atualizado com sucesso no KSC."
        )
    except Exception as e:
        log_json(run_logger, "fix_auth_failed", error=str(e))
        raise OpsError(
            f"Falha operacional ao reconfigurar credenciais administrativas: {e}"
        )
    finally:
        if client:
            client.close()
