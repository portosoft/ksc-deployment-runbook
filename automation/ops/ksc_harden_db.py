# -*- coding: utf-8 -*-
"""
Script Operacional para hardening do banco PostgreSQL remoto do KSC.
"""

import logging
from automation.python.config import KscConfig
from automation.python.remote import (
    connect_ksc_host,
    run_remote_sudo,
    run_remote_sudo_batch,
)
from automation.python.logging_utils import (
    init_evidence_dir,
    configure_logger,
    log_json,
)
from automation.ops.purge_iam_mfa import OpsError

logger = logging.getLogger(__name__)


def apply_hardening(config: KscConfig, apply: bool = False) -> None:
    """
    Verifica ou aplica configurações de hardening no arquivo postgresql.conf.
    Se apply for False, conecta e realiza a validação real (diff) do arquivo.
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

    harden_cmds = [
        'sed -i "s/^#max_connections = .*/max_connections = 1000/" /var/lib/pgsql/16/data/postgresql.conf',
        'sed -i "s/^max_connections = .*/max_connections = 1000/" /var/lib/pgsql/16/data/postgresql.conf',
        "grep -q 'shared_preload_libraries' /var/lib/pgsql/16/data/postgresql.conf || echo \"shared_preload_libraries = 'pg_stat_statements'\" >> /var/lib/pgsql/16/data/postgresql.conf",
        "systemctl restart postgresql-16",
    ]

    client = None
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        # Validação real: lê o arquivo postgresql.conf do host remoto
        cat_cmd = "cat /var/lib/pgsql/16/data/postgresql.conf"
        log_json(run_logger, "run_command_start", cmd=cat_cmd)
        out, err, status = run_remote_sudo(client, cat_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stderr=err)

        if status != 0:
            raise OpsError(f"Falha ao ler o arquivo postgresql.conf remoto: {err}")

        # Parsing de configurações existentes no postgresql.conf
        max_conn_configured = False
        shared_preload_configured = False

        for line in out.splitlines():
            line = line.strip()
            # Ignora linhas comentadas
            if line.startswith("#"):
                continue
            if line.startswith("max_connections") and "1000" in line:
                max_conn_configured = True
            if (
                line.startswith("shared_preload_libraries")
                and "pg_stat_statements" in line
            ):
                shared_preload_configured = True

        if not apply:
            run_logger.info("=== RESULTADO DA VERIFICAÇÃO DE HARDENING ===")
            if max_conn_configured:
                run_logger.info("[OK] max_connections já está configurado como 1000.")
            else:
                run_logger.info(
                    "[MUDANÇA REQUERIDA] max_connections será alterado para 1000."
                )

            if shared_preload_configured:
                run_logger.info(
                    "[OK] shared_preload_libraries já contém pg_stat_statements."
                )
            else:
                run_logger.info(
                    "[MUDANÇA REQUERIDA] shared_preload_libraries = 'pg_stat_statements' será adicionado."
                )

            log_json(
                run_logger,
                "db_hardening_check_only",
                max_conn_ok=max_conn_configured,
                shared_preload_ok=shared_preload_configured,
            )
            return

        # Executa as alterações se necessário
        if max_conn_configured and shared_preload_configured:
            run_logger.info(
                "Hardening do banco de dados já está totalmente aplicado. Nenhuma alteração pendente."
            )
            log_json(run_logger, "db_hardening_already_applied")
            return

        run_logger.info("Aplicando configurações de hardening no PostgreSQL...")
        log_json(run_logger, "run_batch_start", cmds=harden_cmds)
        status, out, err, failed_indices = run_remote_sudo_batch(
            client, harden_cmds, config.ksc_pass
        )
        log_json(
            run_logger,
            "run_batch_end",
            status=status,
            stdout=out,
            stderr=err,
            failed_indices=failed_indices,
        )

        if len(failed_indices) > 0 or status != 0:
            for idx in failed_indices:
                run_logger.error(f"Comando falhou no lote: {harden_cmds[idx]}")
            raise OpsError("Falha ao aplicar comandos de hardening no banco de dados.")

        log_json(run_logger, "db_hardening_success")
        run_logger.info(
            "Hardening do banco de dados PostgreSQL aplicado e serviço reiniciado com sucesso."
        )

    except Exception as e:
        log_json(run_logger, "db_hardening_failed", error=str(e))
        raise OpsError(f"Falha operacional ao executar hardening: {e}")
    finally:
        if client:
            client.close()
