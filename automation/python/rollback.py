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
from typing import List, Optional

from .config import KscConfig
from .setup_steps import (  # noqa: F401
    KSC_ADMINS_GROUP,
    KSC_DATA_DIR,
    KSC_SERVICE_USER,
    KSC_SERVICES,
    SYSTEMD_DROPIN_DIR,
    WEB_CONSOLE_DROPIN_DIR,
    WEB_CONSOLE_SERVICES,
    WEB_CONSOLE_SETUP_FILE,
    SetupError,
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
    """Filtra as unidades que de fato existem no host.

    Uma consulta que falha **não** é tratada como unidade ausente: isso faria o
    rollback deixar de pará-la e a verificação deixar de reportá-la, com a CLI
    anunciando um host limpo sem base para tanto.

    Raises:
        RollbackError: Se alguma unidade não puder ser consultada.
    """
    presentes = []
    for unit in candidates:
        try:
            stdout, _, rc = run_command(
                ["systemctl", "list-unit-files", unit], check=False
            )
        except Exception as e:  # noqa: BLE001 - qualquer falha aqui é indeterminação
            raise RollbackError(
                f"Não foi possível consultar a unidade {unit}: {e}. "
                "O estado do host é indeterminado; nada foi removido."
            )
        if rc == 0 and unit in (stdout or ""):
            presentes.append(unit)
    return presentes


def _psql_cmd(config: Optional[KscConfig], *extra: str) -> List[str]:
    """Monta a invocação do psql usando o endpoint declarado na configuração.

    Sem -h/-p o psql usa o endpoint local padrão. Com um db_port diferente do
    padrão, as operações destrutivas e a verificação atingiriam outro cluster
    que não o do KSC.
    """
    cmd = ["runuser", "-u", "postgres", "--", "psql", "-v", "ON_ERROR_STOP=1", "-q"]
    if config is not None:
        cmd += ["-h", config.db_host, "-p", str(config.db_port)]
    return cmd + list(extra)


def _psql_postgres(
    sql: str, config: KscConfig, logger: logging.Logger, dry_run: bool
) -> None:
    """Executa SQL administrativo como o usuário postgres, via stdin."""
    _run(_psql_cmd(config), logger, dry_run, input_data=sql)


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
    falhas: List[str] = []

    unidades = _existing_units(WEB_CONSOLE_SERVICES + KSC_SERVICES)
    if unidades:
        logger.info(f"Parando {len(unidades)} unidade(s) do KSC...")
        for unit in unidades:
            rc = _run(
                ["systemctl", "disable", "--now", unit], logger, dry_run, check=False
            )
            if rc != 0:
                falhas.append(f"parar a unidade {unit}")
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
        if (
            _run(["dnf", "remove", "-y"] + instalados, logger, dry_run, check=False)
            != 0
        ):
            falhas.append(f"remover os pacotes {instalados}")
    else:
        logger.info("Nenhum pacote do KSC instalado.")

    # 3. Bases de dados. Só faz sentido em PostgreSQL local: em banco remoto a
    #    remoção é decisão do administrador daquele servidor.
    if config.db_host in ("127.0.0.1", "localhost", "::1"):
        for base in KSC_DATABASES:
            # Encerrar conexões antes do DROP: uma sessão remanescente faz o
            # comando falhar com "database is being accessed by other users".
            try:
                _psql_postgres(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    f"WHERE datname = '{base}' AND pid <> pg_backend_pid();",
                    config,
                    logger,
                    dry_run,
                )
                _psql_postgres(
                    f'DROP DATABASE IF EXISTS "{base}";', config, logger, dry_run
                )
            except SetupError as e:
                falhas.append(f"remover a base {base}: {e}")

        try:
            _psql_postgres(
                f'DROP ROLE IF EXISTS "{config.db_user}";', config, logger, dry_run
            )
        except SetupError as e:
            falhas.append(f"remover a role {config.db_user}: {e}")
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
            if _run(["rm", "-rf", caminho], logger, check=False) != 0:
                falhas.append(f"remover {caminho}")
        else:
            logger.info(f"Ausente, nada a remover: {caminho}")

    # 5. Drop-ins systemd. Sem isto sobrevivem diretórios que estendem
    #    unidades inexistentes, poluindo o host e confundindo a próxima
    #    instalação.
    for dropin in (SYSTEMD_DROPIN_DIR, WEB_CONSOLE_DROPIN_DIR):
        if dry_run:
            logger.info(f"[CHECK] Seria removido o drop-in: {dropin}")
        elif Path(dropin).exists():
            if _run(["rm", "-rf", dropin], logger, check=False) != 0:
                falhas.append(f"remover o drop-in {dropin}")
    if _run(["systemctl", "daemon-reload"], logger, dry_run, check=False) != 0:
        falhas.append("recarregar as unidades do systemd")

    # 6. Contas de sistema, por último: removê-las antes faria os passos
    #    anteriores perderem o dono dos arquivos que ainda precisam apagar.
    if dry_run:
        logger.info(
            f"[CHECK] Seriam removidos a conta '{KSC_SERVICE_USER}' e o grupo "
            f"'{KSC_ADMINS_GROUP}', se existirem."
        )
    else:
        if _account_exists("passwd", KSC_SERVICE_USER):
            if _run(["userdel", KSC_SERVICE_USER], logger, check=False) != 0:
                falhas.append(f"remover a conta {KSC_SERVICE_USER}")
        if _account_exists("group", KSC_ADMINS_GROUP):
            if _run(["groupdel", KSC_ADMINS_GROUP], logger, check=False) != 0:
                falhas.append(f"remover o grupo {KSC_ADMINS_GROUP}")

    # Sem isto, um rollback que falhou em vários passos ainda terminava com
    # 'rollback_success' no log de evidências.
    if falhas:
        raise RollbackError(
            "Rollback incompleto — não foi possível: " + "; ".join(falhas)
        )

    logger.info("Rollback concluído.")


def verify_rollback(
    logger: logging.Logger, config: Optional[KscConfig] = None
) -> List[str]:
    """Verifica se sobrou algum resíduo e retorna a lista do que foi encontrado.

    Args:
        logger: Logger da execução.
        config: Configuração do KSC, usada para alcançar o PostgreSQL correto.

    Returns:
        Lista de descrições dos resíduos. Vazia quando o host está limpo.
        Uma verificação que não conseguiu inspecionar algo reporta isso como
        resíduo, e não como ausência dele.
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

    remoto = config is not None and config.db_host not in (
        "127.0.0.1",
        "localhost",
        "::1",
    )
    if remoto:
        # perform_rollback preserva deliberadamente as bases em servidor remoto.
        # Inspecioná-las aqui reportaria como resíduo o que foi preservado de
        # propósito, fazendo --verify falhar sempre nesse cenário.
        logger.info(
            f"PostgreSQL remoto em {config.db_host}: bases fora do escopo da "
            "verificação, por terem sido preservadas deliberadamente."
        )
        for item in residuos:
            logger.warning(f"Resíduo: {item}")
        return residuos

    consulta = "SELECT datname FROM pg_database WHERE datname IN ('ksc', 'ksciam')"
    try:
        stdout, stderr, rc = run_command(
            _psql_cmd(config, "-tAc", consulta), check=False
        )
        if rc == 0:
            for base in (stdout or "").split():
                residuos.append(f"base de dados presente: {base}")
        else:
            # Não conseguir inspecionar não é o mesmo que não haver resíduo:
            # silenciar aqui faria a CLI anunciar um host limpo sem base para isso.
            residuos.append(
                f"não foi possível inspecionar o PostgreSQL (rc={rc}): "
                f"{(stderr or '').strip() or 'sem detalhe'}"
            )
    except Exception as e:
        residuos.append(f"não foi possível inspecionar o PostgreSQL: {e}")

    for item in residuos:
        logger.warning(f"Resíduo: {item}")

    return residuos
