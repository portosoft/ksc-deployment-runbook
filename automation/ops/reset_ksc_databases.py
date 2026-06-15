# -*- coding: utf-8 -*-
"""
Script Operacional para reset e reinicialização de bancos de dados KSC.
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


def reset_ksc_databases(config: KscConfig, apply: bool = False) -> None:
    """
    Termina conexões e reconstrói os bancos ksc e ksciam do PostgreSQL.
    Se apply for False, apenas simula (--check).
    """
    evidence_dir = init_evidence_dir("reset_db")
    run_logger = configure_logger(evidence_dir)
    log_json(
        run_logger,
        "reset_db_start",
        host=config.ksc_host,
        user=config.ksc_user,
        apply=apply,
    )

    dbs = ["ksc", "ksciam"]

    if not apply:
        run_logger.info(
            "[CHECK] Os serviços (kladminserver_srv, ksc-web-console, kliam_srv) seriam parados."
        )
        for db in dbs:
            run_logger.info(
                f"[CHECK] Conexões ativas com o banco '{db}' seriam terminadas."
            )
            run_logger.info(f"[CHECK] O banco '{db}' seria excluído (DROP DATABASE).")
            run_logger.info(
                f"[CHECK] O banco '{db}' seria recriado com owner '{config.db_user}' (CREATE DATABASE)."
            )
        log_json(run_logger, "reset_db_check_only")
        return

    client = None
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        # Para os serviços KSC
        stop_cmd = "systemctl stop kladminserver_srv ksc-web-console kliam_srv"
        log_json(run_logger, "run_command_start", cmd=stop_cmd)
        out, err, status = run_remote_sudo(client, stop_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stdout=out, stderr=err)
        if status != 0:
            raise OpsError(f"Falha ao parar serviços KSC: {err}")

        # Drop e Recreate
        for db in dbs:
            # Terminar conexões ativas
            term_cmd = (
                f'-u postgres psql -c "'
                f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
                f"FROM pg_stat_activity "
                f"WHERE pg_stat_activity.datname = '{db}' "
                f'AND pid <> pg_backend_pid();"'
            )
            log_json(
                run_logger, "run_command_start", cmd=f"terminate connections to {db}"
            )
            out, err, status = run_remote_sudo(client, term_cmd, config.ksc_pass)
            log_json(
                run_logger, "run_command_end", status=status, stdout=out, stderr=err
            )
            if status != 0:
                run_logger.warning(
                    f"Aviso ao terminar conexões com o banco {db}: {err}"
                )

            # Drop database
            drop_cmd = f'-u postgres psql -c "DROP DATABASE {db};"'
            log_json(run_logger, "run_command_start", cmd=f"DROP DATABASE {db}")
            out, err, status = run_remote_sudo(client, drop_cmd, config.ksc_pass)
            log_json(
                run_logger, "run_command_end", status=status, stdout=out, stderr=err
            )
            if status != 0:
                raise OpsError(f"Falha no DROP DATABASE {db}: {err}")

            # Create database
            create_cmd = (
                f'-u postgres psql -c "CREATE DATABASE {db} OWNER {config.db_user};"'
            )
            log_json(run_logger, "run_command_start", cmd=f"CREATE DATABASE {db}")
            out, err, status = run_remote_sudo(client, create_cmd, config.ksc_pass)
            log_json(
                run_logger, "run_command_end", status=status, stdout=out, stderr=err
            )
            if status != 0:
                raise OpsError(f"Falha no CREATE DATABASE {db}: {err}")

        log_json(run_logger, "reset_db_success")
        run_logger.info("Bancos de dados KSC limpos e recriados com sucesso.")
    except Exception as e:
        log_json(run_logger, "reset_db_failed", error=str(e))
        raise OpsError(f"Falha operacional ao resetar bancos: {e}")
    finally:
        if client:
            client.close()
