# -*- coding: utf-8 -*-
"""
Script Operacional para reconfiguração dos serviços do KSC.
"""

import logging
import uuid
from automation.python.config import KscConfig
from automation.python.remote import connect_ksc_host, run_remote_sudo
from automation.python.logging_utils import (
    init_evidence_dir,
    configure_logger,
    log_json,
)
from automation.ops.purge_iam_mfa import OpsError

logger = logging.getLogger(__name__)


def reconfigure_ksc_service(config: KscConfig, apply: bool = False) -> None:
    """
    Gera um arquivo de resposta temporário seguro e executa o postinstall.pl do KSC.
    Se apply for False, apenas simula (--check).
    """
    evidence_dir = init_evidence_dir("reconfigure_service")
    run_logger = configure_logger(evidence_dir)
    log_json(
        run_logger,
        "reconfigure_start",
        host=config.ksc_host,
        user=config.ksc_user,
        apply=apply,
    )

    # Conteúdo do arquivo de respostas (gerado dinamicamente com valores seguros)
    ans_content = f"""EULA_ACCEPTED=1
PP_ACCEPTED=1
KSN_ACCEPTED=1
KLSRV_UNATT_DBMS_TYPE=Postgres
KLSRV_UNATT_DBMS_INSTANCE=127.0.0.1
KLSRV_UNATT_DBMS_PORT=5432
KLSRV_UNATT_DBMS_LOGIN=kluser
KLSRV_UNATT_DBMS_PASSWORD={config.db_password}
KLSRV_UNATT_DB_NAME=ksc
KLSRV_UNATT_DBMS_IAM_TYPE=Postgres
KLSRV_UNATT_DBMS_IAM_INSTANCE=127.0.0.1
KLSRV_UNATT_DBMS_IAM_PORT=5432
KLSRV_UNATT_DBMS_IAM_LOGIN=kluser
KLSRV_UNATT_DBMS_IAM_PASSWORD={config.db_password}
KLSRV_UNATT_DB_IAM_NAME=ksciam
KLSRV_UNATT_SERVERADDRESS={config.ksc_fqdn}
KLSRV_UNATT_IAM_ADDRESS=127.0.0.1
KLSRV_UNATT_KLSVCUSER=ksc
KLSRV_UNATT_KLADMINSGROUP=kladmins
KLSRV_UNATT_KLIAMUSER=ksc
KLSRV_UNATT_KLSRVUSER=ksc
KLSRV_UNATT_KLADMINS_USER={config.ksc_admin_user}
KLSRV_UNATT_KLADMINS_PASSWORD={config.ksc_admin_password}
"""

    ans_file = f"/tmp/reconfig_ans_{uuid.uuid4().hex}.txt"

    if not apply:
        run_logger.info(
            f"[CHECK] Seria gerado um arquivo de respostas KLAUTOANSWERS em '{ans_file}' via SFTP (modo 0600)."
        )
        run_logger.info(
            f"[CHECK] Seria executado: KLAUTOANSWERS={ans_file} /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl"
        )
        run_logger.info(
            f"[CHECK] O arquivo temporário '{ans_file}' seria removido do servidor remoto."
        )
        run_logger.info(
            "[CHECK] Os serviços (kladminserver_srv.service e ksc-web-console.service) seriam reiniciados."
        )
        log_json(run_logger, "reconfigure_check_only")
        return

    client = None
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        # Upload do arquivo de respostas via SFTP de forma isolada e segura
        run_logger.info(
            f"Gerando arquivo de respostas em {ans_file} via SFTP..."
        )
        sftp = client.open_sftp()
        f = sftp.file(ans_file, "w")
        # Força permissão apenas de leitura/escrita pelo owner para evitar vazamento local
        f.chmod(0o600)
        f.write(ans_content)
        f.close()
        sftp.close()

        # Executa postinstall.pl
        postinstall_cmd = (
            f"KLAUTOANSWERS={ans_file} "
            "/opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl"
        )
        run_cmd = f"-E bash -c '{postinstall_cmd}'"
        log_json(run_logger, "run_command_start", cmd="postinstall.pl (silencioso)")

        out, err, status = run_remote_sudo(
            client, run_cmd, config.ksc_pass
        )
        if out:
            for line in out.splitlines():
                run_logger.info(line.strip())
        log_json(run_logger, "run_command_end", status=status, stderr=err)

        # Limpeza do arquivo temporário
        client.exec_command(f"rm -f {ans_file}")

        if status != 0:
            raise OpsError(f"Erro na execução do postinstall.pl: {err}")

        # Reinicia serviços
        restart_cmd = (
            "systemctl restart kladminserver_srv.service ksc-web-console.service"
        )
        log_json(run_logger, "run_command_start", cmd=restart_cmd)
        out, err, status = run_remote_sudo(client, restart_cmd, config.ksc_pass)
        log_json(run_logger, "run_command_end", status=status, stdout=out, stderr=err)

        if status != 0:
            raise OpsError(f"Falha ao reiniciar os serviços KSC: {err}")

        log_json(run_logger, "reconfigure_success")
        run_logger.info("Reconfiguração dos serviços concluída com sucesso.")
    except Exception as e:
        log_json(run_logger, "reconfigure_failed", error=str(e))
        raise OpsError(f"Falha ao reconfigurar os serviços: {e}")
    finally:
        if client:
            client.close()
