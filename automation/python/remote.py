# -*- coding: utf-8 -*-
"""
Módulo de Execução Remota SSH (Paramiko) para KSC Runbook.
Fornece abstração segura de conexão e comandos sudo remotos.
"""

import logging
import shlex
import paramiko
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


def connect_ksc_host(
    host: str, user: str, password: str, timeout: int = 15
) -> paramiko.SSHClient:
    """
    Cria uma conexão SSH segura com o host usando as credenciais fornecidas.
    Garante a política estrita de RejectPolicy para chaves de host.
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        logger.info(f"Conectando via SSH a {user}@{host}...")
        client.connect(hostname=host, username=user, password=password, timeout=timeout)
        return client
    except Exception as e:
        logger.error(f"Falha na conexão SSH com {host}: {e}")
        raise


def run_remote_sudo(
    client: paramiko.SSHClient,
    cmd: str,
    password: str,
    stdin_inputs: Optional[List[str]] = None,
) -> Tuple[str, str, int]:
    """
    Executa um comando remoto com sudo, enviando a senha via stdin
    para evitar exposição na lista de processos do servidor.
    Se stdin_inputs for fornecido, insere sequencialmente as linhas adicionais no stdin.
    """
    sudo_cmd = f"sudo -S {cmd}"
    stdin, stdout, stderr = client.exec_command(sudo_cmd)

    try:
        # Envia a senha do sudo primeiro
        stdin.write(password + "\n")

        # Envia entradas adicionais se existirem
        if stdin_inputs:
            for item in stdin_inputs:
                stdin.write(item + "\n")

        stdin.flush()
        stdin.channel.shutdown_write()

        out = stdout.read().decode("utf-8", errors="ignore").strip()
        err = stderr.read().decode("utf-8", errors="ignore").strip()
        status = stdout.channel.recv_exit_status()

        return out, err, status
    except Exception as e:
        logger.error(f"Erro ao executar comando remoto '{cmd}': {e}")
        raise


def run_remote_sudo_batch(
    client: paramiko.SSHClient, cmds: List[str], password: str
) -> Tuple[int, str, str, List[int]]:
    """
    Executa uma lista de comandos remotos sob o mesmo contexto sudo usando sh -c
    e detecta falhas individuais via marcadores __KSC_FAIL__:{i}.
    Retorna (status_final, out, err, indices_dos_comandos_que_falharam).
    """
    script_lines = []
    for i, cmd in enumerate(cmds):
        script_lines.append(cmd)
        script_lines.append(f"if [ $? -ne 0 ]; then echo '__KSC_FAIL__:{i}' >&2; fi")

    batch_cmd = "\n".join(script_lines)
    escaped_batch = shlex.quote(batch_cmd)

    stdin, stdout, stderr = client.exec_command(f"sudo -S sh -c {escaped_batch}")

    try:
        stdin.write(password + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()

        status = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="ignore").strip()
        err = stderr.read().decode("utf-8", errors="ignore").strip()

        failed_indices = []
        for line in err.splitlines():
            if line.startswith("__KSC_FAIL__:"):
                try:
                    idx = int(line.split(":")[1])
                    failed_indices.append(idx)
                except (IndexError, ValueError):
                    pass

        return status, out, err, failed_indices
    except Exception as e:
        logger.error(f"Erro ao executar lote de comandos remotos: {e}")
        raise
