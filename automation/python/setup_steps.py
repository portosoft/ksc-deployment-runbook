import logging

from .checks import CheckResult, run_precheck
from .config import KscConfig
from .shell_utils import ShellCommandError, run_command


class SetupError(Exception):
    pass


def _set_selinux_mode(mode: str, logger: logging.Logger) -> None:
    """Configura o modo do SELinux via setenforce (0 ou 1)."""
    try:
        run_command(["setenforce", mode])
        logger.info(f"SELinux alterado para modo: {mode}")
    except ShellCommandError as e:
        logger.warning(
            f"Aviso: Falha ao tentar mudar SELinux para {mode}. Talvez não instalado? Erro: {e}"
        )


def _get_selinux_mode() -> str:
    """Obtém o modo atual do SELinux via getenforce."""
    try:
        stdout, _, rc = run_command(["getenforce"], check=False)
        if rc == 0:
            return stdout.strip().lower()
    except Exception:
        pass
    return "unknown"


def ensure_os_prereqs(config: KscConfig, logger: logging.Logger) -> None:
    """Verifica e instala pré-requisitos do SO (mock em ambiente de desenvolvimento).

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.
    """
    logger.info("Verificando/instalando pré-requisitos do SO...")
    # Exemplo real seria: run_command(["dnf", "install", "-y", "tar", "curl", "wget"])
    logger.info("[Mock] Pré-requisitos instalados.")


def setup_postgres(config: KscConfig, logger: logging.Logger) -> None:
    """Configura o PostgreSQL 16 para uso pelo KSC (mock).

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.
    """
    logger.info("Configurando PostgreSQL...")
    # Aqui entraria a chamada ao script ansible ou psql real
    logger.info("[Mock] PostgreSQL 16 provisionado e preparado.")


def verify_ksc_packages(package_dir: str, logger: logging.Logger) -> None:
    """Verifica a integridade criptográfica SHA-256 dos pacotes RPM antes da instalação.

    Args:
        package_dir: Diretório contendo os arquivos RPM a serem verificados.
        logger: Logger para registro das operações.

    Raises:
        SetupError: Se qualquer pacote reconhecido apresentar hash divergente.
    """
    from .packages import verify_directory

    logger.info(f"Verificando integridade SHA-256 dos pacotes em '{package_dir}'...")
    try:
        results = verify_directory(package_dir)
    except Exception as e:
        raise SetupError(f"Falha ao validar diretório de pacotes '{package_dir}': {e}")

    if results["failed"]:
        failed_files = [item["file"] for item in results["failed"]]
        logger.error(f"Pacotes com checksum divergente detectados: {failed_files}")
        raise SetupError(
            f"Falha de integridade criptográfica nos pacotes: {', '.join(failed_files)}. "
            "Possível corrupção ou adulteração de binários."
        )

    logger.info(
        f"Integridade validada com sucesso: {len(results['verified'])} pacotes certificados."
    )


def install_ksc_server(config: KscConfig, logger: logging.Logger) -> None:
    """Instala o KSC Server e Web Console via RPM silencioso (mock).

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.
    """
    import os

    packages_dir = getattr(config, "packages_dir", None) or os.environ.get(
        "KSC_PACKAGES_DIR"
    )
    if not packages_dir:
        raise SetupError(
            "KSC_PACKAGES_DIR não configurado. A verificação prévia de integridade dos pacotes é obrigatória para instalação."
        )
    verify_ksc_packages(packages_dir, logger)

    logger.info("Instalando KSC Server e Web Console...")
    # Wrapper real de instalação silenciosa
    logger.info("[Mock] KSC Server RPM instalado.")
    logger.info(
        "Nota sobre LD_LIBRARY_PATH: O KSC no Linux muitas vezes exige bibliotecas. A recomendação DEVSECOPS é usar Environment=LD_LIBRARY_PATH=... no arquivo de serviço systemd, nunca em /etc/profile ou /etc/environment, para evitar vazamento global."
    )


def post_install_hardening(config: KscConfig, logger: logging.Logger) -> None:
    """Aplica hardening pós-instalação: permissões, SELinux, serviços (mock).

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.
    """
    logger.info("Aplicando hardening pós-instalação...")
    logger.info("[Mock] Permissões em /opt/kaspersky restritas.")


def perform_precheck_only(config: KscConfig, logger: logging.Logger) -> CheckResult:
    """Executa apenas os pré-checks sem iniciar a instalação. Retorna CheckResult.

    Args:
        config: Configuração do KSC.
        logger: Logger para registro das operações.

    Returns:
        CheckResult com os resultados dos pré-checks.
    """
    return run_precheck(config)


def perform_setup(config: KscConfig, logger: logging.Logger) -> None:
    """Orquestra a instalação garantindo o ciclo seguro do SELinux."""
    original_selinux = _get_selinux_mode()
    selinux_changed = False

    try:
        # Prechecks
        result = perform_precheck_only(config, logger)
        if result.has_critical:
            raise SetupError(
                "Prechecks falharam criticamente. Interrompendo instalação."
            )

        # Temporariamente permissivo para a instalação não falhar no setup de binários
        if original_selinux == "enforcing":
            logger.info(
                "Desabilitando SELinux (permissive) temporariamente para a instalação do KSC."
            )
            _set_selinux_mode("0", logger)
            selinux_changed = True

        ensure_os_prereqs(config, logger)
        setup_postgres(config, logger)
        install_ksc_server(config, logger)
        post_install_hardening(config, logger)

    except Exception as e:
        raise SetupError(f"Falha na instalação: {e}")
    finally:
        if selinux_changed:
            logger.info(
                "Restaurando SELinux para o modo enforcing (Segurança por Padrão)."
            )
            _set_selinux_mode("1", logger)

        # O ideal aqui é chamar o restorecon recursivo na pasta do kaspersky:
        # run_command(["restorecon", "-Rv", "/opt/kaspersky"], check=False)
