# -*- coding: utf-8 -*-
"""
Script Operacional para hardening do banco PostgreSQL remoto do KSC via SQL nativo.
"""

import logging
import shlex

from automation.ops.purge_iam_mfa import OpsError
from automation.python.config import KscConfig
from automation.python.logging_utils import (
    configure_logger,
    init_evidence_dir,
    log_json,
)
from automation.python.remote import connect_ksc_host, run_remote_sudo

logger = logging.getLogger(__name__)


def apply_hardening(config: KscConfig, apply: bool = False) -> None:
    """
    Aplica configurações de hardening no PostgreSQL via SQL nativo (ALTER SYSTEM).
    Se apply for False, apenas simula (--check).
    """
    evidence_dir = init_evidence_dir("db_hardening")
    run_logger = configure_logger(evidence_dir)
    log_json(
        run_logger,
        "db_hardening_start",
        host=config.ksc_host,
        user=config.ksc_user,
        apply=apply,
    )

    queries = [
        "ALTER SYSTEM SET max_connections = 1000;",
        "ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';",
        "SELECT pg_reload_conf();",
    ]
    restart_cmd = "systemctl restart postgresql-16"

    if not apply:
        run_logger.info("[CHECK] Os seguintes comandos SQL seriam executados no Postgres:")
        for q in queries:
            run_logger.info(f"  - {q}")
        run_logger.info(f"[CHECK] O serviço seria reiniciado: {restart_cmd}")
        log_json(run_logger, "db_hardening_check_only")
        return

    client = None
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        for q in queries:
            sql_cmd = f"-u postgres psql -c {shlex.quote(q)}"
            log_json(run_logger, "run_command_start", cmd=f"psql -c {shlex.quote(q)}")
            out, err, status = run_remote_sudo(client, sql_cmd, config.ksc_pass)
            log_json(
                run_logger, "run_command_end", status=status, stdout=out, stderr=err
            )
            if status != 0:
                raise OpsError(f"Falha ao executar query no Postgres: {err}")

        # Reinicia o serviço postgresql-16
        log_json(run_logger, "run_command_start", cmd=restart_cmd)
        out, err, status = run_remote_sudo(client, restart_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stdout=out, stderr=err)
        if status != 0:
            raise OpsError(f"Falha ao reiniciar o serviço postgresql-16: {err}")

        log_json(run_logger, "db_hardening_success")
        run_logger.info("Hardening do PostgreSQL aplicado e serviço reiniciado com sucesso.")

    except Exception as e:
        log_json(run_logger, "db_hardening_failed", error=str(e))
        raise OpsError(f"Falha operacional ao executar hardening: {e}")
    finally:
        if client:
            client.close()
