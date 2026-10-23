# -*- coding: utf-8 -*-
"""
Script Operacional para validação/teste de acesso sudo remoto.
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


def test_sudo(config: KscConfig, apply: bool = False) -> None:
    """
    Executa um comando simples (whoami) sob sudo no host remoto para testar conectividade e privilégios.
    Se apply for False, apenas simula (--check).
    """
    evidence_dir = init_evidence_dir("test_sudo")
    run_logger = configure_logger(evidence_dir)
    log_json(
        run_logger,
        "test_sudo_start",
        host=config.ksc_host,
        user=config.ksc_user,
        apply=apply,
    )

    if not apply:
        run_logger.info(
            "[CHECK] Seria iniciada uma conexão SSH para validar conectividade."
        )
        run_logger.info(
            "[CHECK] Seria executado 'whoami' sob sudo para verificar privilégios de root."
        )
        log_json(run_logger, "test_sudo_check_only")
        return

    client = None
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        # Executa o whoami sob sudo
        log_json(run_logger, "run_command_start", cmd="whoami")
        out, err, status = run_remote_sudo(client, "whoami", config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stdout=out, stderr=err)

        if status != 0:
            raise OpsError(f"Erro ao obter privilégios sudo no host remoto: {err}")

        run_logger.info(
            f"Conectividade e privilégios OK. Usuário retornado pelo sudo remoto: {out}"
        )
        log_json(run_logger, "test_sudo_success", sudo_user=out)
    except Exception as e:
        log_json(run_logger, "test_sudo_failed", error=str(e))
        raise OpsError(f"Falha ao validar privilégios do sudo remoto: {e}")
    finally:
        if client:
            client.close()
