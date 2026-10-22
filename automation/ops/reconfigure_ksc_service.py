# -*- coding: utf-8 -*-
"""
Script Operacional para reconfiguração dos serviços do KSC.
"""

import logging
import uuid
from automation.python.config import KscConfig
from automation.python.remote import connect_ksc_host, run_remote_sudo
from automation.python.setup_steps import build_response_file
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
    ans_dir = f"/tmp/reconfig_ksc_{uuid.uuid4().hex}"
    ans_file = f"{ans_dir}/answers.txt"
    evidence_dir = init_evidence_dir("reconfigure_service")
    run_logger = configure_logger(evidence_dir)
    log_json(
        run_logger,
        "reconfigure_start",
        host=config.ksc_host,
        user=config.ksc_user,
        apply=apply,
    )

    # Fonte única do formato KLAUTOANSWERS, compartilhada com a instalação inicial.
    ans_content = build_response_file(config)

    if not apply:
        run_logger.info(
            f"[CHECK] Seria criado um diretório privado restrito '{ans_dir}' via SFTP (modo 0700)."
        )
        run_logger.info(
            f"[CHECK] Seria gerado um arquivo de respostas KLAUTOANSWERS em '{ans_file}' via SFTP (modo 0600)."
        )
        run_logger.info(
            f"[CHECK] Seria executado: KLAUTOANSWERS={ans_file} /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl"
        )
        run_logger.info(
            f"[CHECK] O diretório temporário '{ans_dir}' e o arquivo '{ans_file}' seriam removidos do servidor remoto."
        )
        run_logger.info(
            "[CHECK] Os serviços (kladminserver_srv.service e ksc-web-console.service) seriam reiniciados."
        )
        log_json(run_logger, "reconfigure_check_only")
        return

    client = None
    remote_dir_created = False
    try:
        client = connect_ksc_host(config.ksc_host, config.ksc_user, config.ksc_pass)

        # Upload do arquivo de respostas via SFTP dentro de diretório restrito 0700 (mitigação TOCTOU)
        run_logger.info(
            f"Criando diretório seguro {ans_dir} e gerando arquivo de respostas em {ans_file} via SFTP..."
        )
        sftp = client.open_sftp()
        sftp.mkdir(ans_dir, mode=0o700)
        remote_dir_created = True

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
            if remote_dir_created:
                sftp_cleaned = False
                try:
                    sftp_cleanup = client.open_sftp()
                    try:
                        sftp_cleanup.remove(ans_file)
                    except Exception:
                        pass
                    try:
                        sftp_cleanup.rmdir(ans_dir)
                    except Exception:
                        pass
                    sftp_cleanup.close()
                    sftp_cleaned = True
                except Exception:
                    pass

                try:
                    _, _, stderr = client.exec_command(
                        f"rm -f '{ans_file}' && rmdir '{ans_dir}'"
                    )
                    status = stderr.channel.recv_exit_status()
                    if status != 0 and not sftp_cleaned:
                        run_logger.warning(
                            f"Falha na limpeza do diretório remoto temporário '{ans_dir}' (código {status})."
                        )
                except Exception as cleanup_err:
                    if not sftp_cleaned:
                        run_logger.warning(
                            f"Erro ao tentar remover diretório remoto temporário '{ans_dir}': {cleanup_err}"
                        )
            client.close()
