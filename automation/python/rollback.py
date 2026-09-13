# -*- coding: utf-8 -*-
"""
Rollback do KSC 16.x: devolve o host ao estado anterior ao deploy.

Executa localmente no servidor alvo, como root, e cobre os resíduos que o
procedimento manual de ``docs/11-rollback.md`` deixava para trás — verificados
em rollback real sobre uma instalação do KSC 16.3 em Rocky Linux 9.8 (#223):

- o RPM ``klnagent64``, que o procedimento não removia;
- a base ``ksciam``, citada apenas como ``ksc``;
- a role de aplicação, procurada sob um nome que nunca existiu;
- as contas de sistema ``ksc`` e ``kladmins``;
- ``/etc/ksc-web-console-setup.json`` e ``/var/log/kaspersky``;
- os drop-ins systemd, que sobreviviam às unidades que estendiam.

A operação é destrutiva e irreversível: exige ``--apply`` e o token de
confirmação, como as demais operações destrutivas da CLI.
"""

import logging
from pathlib import Path
from typing import List

from .config import KscConfig
from .setup_steps import (
    KSC_ADMINS_GROUP,
    KSC_DATA_DIR,
    KSC_SERVICES,
    KSC_SERVICE_USER,
    SYSTEMD_DROPIN_DIR,
    WEB_CONSOLE_DROPIN_DIR,
    WEB_CONSOLE_SERVICES,
    WEB_CONSOLE_SETUP_FILE,
    _account_exists,
    _run,
)
from .shell_utils import run_command

# Todos os RPMs do produto. O procedimento manual esquecia o klnagent64, que
# permanecia instalado após um rollback tido como completo.
KSC_RPMS = ["ksc64", "klnagent64", "ksc-web-console"]

# O KSC usa duas bases. A operacional costuma ser removida pelo próprio
# desinstalador do RPM; a do serviço IAM sobrevive e era reaproveitada pela
# instalação seguinte, que assim herdava estado de identidade anterior.
KSC_DATABASES = ["ksc", "ksciam"]

# Diretórios e arquivos deixados para trás pela desinstalação dos pacotes.
KSC_PATHS = [
    "/opt/kaspersky",
    KSC_DATA_DIR,
    "/var/log/kaspersky",
    "/var/lib/ksc-web-console",
]


class RollbackError(Exception):
    pass


def _existing_units(candidates: List[str]) -> List[str]:
    """Filtra as unidades que de fato existem no host."""
    presentes = []
    for unit in candidates:
        try:
            stdout, _, rc = run_command(
                ["systemctl", "list-unit-files", unit], check=False
            )
            if rc == 0 and unit in (stdout or ""):
                presentes.append(unit)
        except Exception:
            continue
    return presentes


def _psql_postgres(sql: str, logger: logging.Logger, dry_run: bool) -> None:
    """Executa SQL administrativo como o usuário postgres, via stdin."""
    _run(
        ["runuser", "-u", "postgres", "--", "psql", "-v", "ON_ERROR_STOP=1", "-q"],
        logger,
        dry_run,
        input_data=sql,
        check=False,
    )


def perform_rollback(
    config: KscConfig, logger: logging.Logger, dry_run: bool = False
) -> None:
    """Remove a instalação do KSC e o estado que ela deixa no host.

    Os passos são tolerantes a ausência: um rollback precisa funcionar tanto
    sobre uma instalação completa quanto sobre uma que falhou pela metade, em
    que boa parte dos artefatos nunca chegou a existir.

    Args:
        config: Configuração do KSC, usada para identificar a role do banco.
        logger: Logger da execução.
        dry_run: Se True, apenas registra o que seria removido.
    """
    logger.info("Iniciando rollback do KSC...")

    # 1. Serviços. Parar antes de remover pacotes evita processos escrevendo
    #    em diretórios que estão sendo apagados e conexões abertas no banco.
    unidades = _existing_units(WEB_CONSOLE_SERVICES + KSC_SERVICES)
    if unidades:
        logger.info(f"Parando {len(unidades)} unidade(s) do KSC...")
        for unit in unidades:
            _run(["systemctl", "disable", "--now", unit], logger, dry_run, check=False)
    else:
        logger.info("Nenhuma unidade do KSC presente.")

    # 2. Pacotes.
    instalados = []
    for rpm in KSC_RPMS:
        _, _, rc = run_command(["rpm", "-q", rpm], check=False)
        if rc == 0:
            instalados.append(rpm)
    if instalados:
        logger.info(f"Removendo pacotes: {instalados}")
        _run(["dnf", "remove", "-y"] + instalados, logger, dry_run, check=False)
    else:
        logger.info("Nenhum pacote do KSC instalado.")

    # 3. Bases de dados. Só faz sentido em PostgreSQL local: em banco remoto a
    #    remoção é decisão do administrador daquele servidor.
    if config.db_host in ("127.0.0.1", "localhost", "::1"):
        for base in KSC_DATABASES:
            # Encerrar conexões antes do DROP: uma sessão remanescente faz o
            # comando falhar com "database is being accessed by other users".
            _psql_postgres(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{base}' AND pid <> pg_backend_pid();",
                logger,
                dry_run,
            )
            _psql_postgres(f'DROP DATABASE IF EXISTS "{base}";', logger, dry_run)

        _psql_postgres(f'DROP ROLE IF EXISTS "{config.db_user}";', logger, dry_run)
    else:
        logger.info(
            f"PostgreSQL remoto em {config.db_host}: bases e role preservadas. "
            "A remoção é responsabilidade do administrador daquele servidor."
        )

    # 4. Diretórios e arquivos de configuração.
    for caminho in KSC_PATHS + [WEB_CONSOLE_SETUP_FILE]:
        if dry_run:
            logger.info(f"[CHECK] Seria removido: {caminho}")
        elif Path(caminho).exists():
            _run(["rm", "-rf", caminho], logger, check=False)
        else:
            logger.info(f"Ausente, nada a remover: {caminho}")

    # 5. Drop-ins systemd. Sem isto sobrevivem diretórios que estendem
    #    unidades inexistentes, poluindo o host e confundindo a próxima
    #    instalação.
    for dropin in (SYSTEMD_DROPIN_DIR, WEB_CONSOLE_DROPIN_DIR):
        if dry_run:
            logger.info(f"[CHECK] Seria removido o drop-in: {dropin}")
        elif Path(dropin).exists():
            _run(["rm", "-rf", dropin], logger, check=False)
    _run(["systemctl", "daemon-reload"], logger, dry_run, check=False)

    # 6. Contas de sistema, por último: removê-las antes faria os passos
    #    anteriores perderem o dono dos arquivos que ainda precisam apagar.
    if dry_run:
        logger.info(
            f"[CHECK] Seriam removidos a conta '{KSC_SERVICE_USER}' e o grupo "
            f"'{KSC_ADMINS_GROUP}', se existirem."
        )
    else:
        if _account_exists("passwd", KSC_SERVICE_USER):
            _run(["userdel", KSC_SERVICE_USER], logger, check=False)
        if _account_exists("group", KSC_ADMINS_GROUP):
            _run(["groupdel", KSC_ADMINS_GROUP], logger, check=False)

    logger.info("Rollback concluído.")


def verify_rollback(logger: logging.Logger) -> List[str]:
    """Verifica se sobrou algum resíduo e retorna a lista do que foi encontrado.

    Returns:
        Lista de descrições dos resíduos. Vazia quando o host está limpo.
    """
    residuos = []

    for rpm in KSC_RPMS:
        _, _, rc = run_command(["rpm", "-q", rpm], check=False)
        if rc == 0:
            residuos.append(f"pacote instalado: {rpm}")

    for caminho in KSC_PATHS + [WEB_CONSOLE_SETUP_FILE]:
        if Path(caminho).exists():
            residuos.append(f"caminho presente: {caminho}")

    for dropin in (SYSTEMD_DROPIN_DIR, WEB_CONSOLE_DROPIN_DIR):
        if Path(dropin).exists():
            residuos.append(f"drop-in systemd presente: {dropin}")

    unidades = _existing_units(WEB_CONSOLE_SERVICES + KSC_SERVICES)
    for unit in unidades:
        residuos.append(f"unidade systemd presente: {unit}")

    if _account_exists("passwd", KSC_SERVICE_USER):
        residuos.append(f"conta de sistema presente: {KSC_SERVICE_USER}")
    if _account_exists("group", KSC_ADMINS_GROUP):
        residuos.append(f"grupo presente: {KSC_ADMINS_GROUP}")

    try:
        stdout, _, rc = run_command(
            [
                "runuser",
                "-u",
                "postgres",
                "--",
                "psql",
                "-tAc",
                "SELECT datname FROM pg_database WHERE datname IN ('ksc', 'ksciam')",
            ],
            check=False,
        )
        if rc == 0:
            for base in (stdout or "").split():
                residuos.append(f"base de dados presente: {base}")
    except Exception:
        pass

    for item in residuos:
        logger.warning(f"Resíduo: {item}")

    return residuos
