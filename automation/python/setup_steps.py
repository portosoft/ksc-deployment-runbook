from .config import KscConfig
from .checks import CheckResult, run_precheck
import logging


class SetupError(Exception):
    pass


def ensure_os_prereqs(config: KscConfig, logger: logging.Logger) -> None:
    logger.info("Verificando/instalando pré-requisitos do SO...")
    # placeholder para lógica real


def setup_postgres(config: KscConfig, logger: logging.Logger) -> None:
    logger.info("Configurando PostgreSQL...")
    # placeholder para lógica real


def install_ksc_server(config: KscConfig, logger: logging.Logger) -> None:
    logger.info("Instalando KSC Server...")
    # placeholder para lógica real


def post_install_hardening(config: KscConfig, logger: logging.Logger) -> None:
    logger.info("Aplicando hardening pós-instalação...")
    # placeholder para lógica real


def perform_precheck_only(config: KscConfig, logger: logging.Logger) -> CheckResult:
    return run_precheck(config)


def perform_setup(config: KscConfig, logger: logging.Logger) -> None:
    try:
        ensure_os_prereqs(config, logger)
        setup_postgres(config, logger)
        install_ksc_server(config, logger)
        post_install_hardening(config, logger)
    except Exception as e:
        raise SetupError(f"Falha na instalação: {e}")
