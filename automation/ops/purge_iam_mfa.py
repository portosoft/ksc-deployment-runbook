# -*- coding: utf-8 -*-
"""
Script Operacional para limpeza (purge) de tabelas de MFA do serviço IAM do KSC.
"""

import logging
from automation.python.config import KscConfig
from automation.python.remote import connect_ksc_host, run_remote_sudo
from automation.python.logging_utils import (
    init_evidence_dir,
    configure_logger,
    log_json,
)

logger = logging.getLogger(__name__)


class OpsError(Exception):
    """Exceção customizada para erros em operações remotas."""

    pass


def purge_iam_mfa(config: KscConfig, apply: bool = False) -> None:
    """
    Limpa as tabelas de MFA do serviço IAM.
    Se apply for False, apenas simula (--check).
    """
    evidence_dir = init_evidence_dir("purge_mfa")
    run_logger = configure_logger(evidence_dir)
    log_json(
        run_logger,
        "purge_mfa_start",
        host=config.ksc_host,
        user=config.ksc_user,
        apply=apply,
    )

    queries = [
        "TRUNCATE iam.authentication_factors CASCADE;",
        "TRUNCATE iam.authentication_factors_secret CASCADE;",
        "TRUNCATE iam.authentication_factors_totp_settings CASCADE;",
    ]

    if not apply:
        run_logger.info(
            "[CHECK] Os seguintes comandos SQL seriam executados no banco 'ksciam' do Postgres:"
        )
        for q in queries:
            run_logger.info(f"  - {q}")
        run_logger.info(
            "[CHECK] Os serviços (kladminserver_srv, kliam_srv, ksc-web-console) seriam reiniciados."
        )
        log_json(run_logger, "purge_mfa_check_only")
        return

    client = None
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        # Executa as queries
        for q in queries:
            sql_cmd = f'-u postgres psql -d ksciam -c "{q}"'
            # Omitir credenciais nos logs do JSON
            log_json(run_logger, "run_command_start", cmd=f'psql -d ksciam -c "{q}"')
            out, err, status = run_remote_sudo(client, sql_cmd, config.ksc_pass)
            log_json(
                run_logger, "run_command_end", status=status, stdout=out, stderr=err
            )

            if status != 0:
                raise OpsError(f"Falha ao executar query no Postgres: {err}")

        # Reinicia os serviços
        restart_cmd = "systemctl restart kladminserver_srv kliam_srv ksc-web-console"
        log_json(run_logger, "run_command_start", cmd=restart_cmd)
        out, err, status = run_remote_sudo(client, restart_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stdout=out, stderr=err)

        if status != 0:
            raise OpsError(f"Falha ao reiniciar os serviços KSC: {err}")

        log_json(run_logger, "purge_mfa_success")
        run_logger.info("Purge de MFA concluído e serviços reiniciados com sucesso.")
    except Exception as e:
        log_json(run_logger, "purge_mfa_failed", error=str(e))
        raise OpsError(f"Falha operacional ao limpar MFA: {e}")
    finally:
        if client:
            client.close()
