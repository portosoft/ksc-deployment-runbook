# -*- coding: utf-8 -*-
"""
Ferramenta CLI Unificada KSCCTL - Entrypoint Operacional do KSC Runbook.
Permite executar auditorias locais, instalação e todas as operações remotas
com auditoria e tokens de confirmação para ações destrutivas.
"""

import argparse
import sys
from typing import List, Optional


def _validate_destructive_confirmation(
    action_name: str,
    base_token: str,
    token_passed: Optional[str],
    target_passed: Optional[str],
    expected_host: str,
) -> bool:
    """Valida se o token e o alvo de confirmação contextual coincidem com o host da operação.

    Aceita:
    - Token exato com ou sem alvo contextual: 'TOKEN' ou 'TOKEN:<host>'.
    - Se informado 'TOKEN:<alvo>', o alvo deve coincidir com expected_host.
    - Se informada a flag --confirm-target, o alvo deve coincidir com expected_host.
    """
    if not token_passed:
        print(
            f"[ERROR] Token de confirmação ausente para '{action_name}'. Use --confirm-token={base_token}:{expected_host}",
            file=sys.stderr,
        )
        return False

    if ":" in token_passed:
        token_action, token_target = token_passed.split(":", 1)
        if token_action != base_token:
            print(
                f"[ERROR] Ação do token '{token_action}' não corresponde à operação esperada '{base_token}'.",
                file=sys.stderr,
            )
            return False
        if token_target != expected_host:
            print(
                f"[ERROR] Alvo contextual do token '{token_target}' diverge do host ativo '{expected_host}'.",
                file=sys.stderr,
            )
            return False
    else:
        if token_passed != base_token:
            print(
                f"[ERROR] Token de confirmação inválido ('{token_passed}'). Esperado '{base_token}' ou '{base_token}:{expected_host}'.",
                file=sys.stderr,
            )
            return False

    if target_passed and target_passed != expected_host:
        print(
            f"[ERROR] Alvo informado em --confirm-target '{target_passed}' diverge do host ativo '{expected_host}'.",
            file=sys.stderr,
        )
        return False

    return True


MIN_PYTHON_VERSION = (3, 10)


def assert_python_version(version_info: Optional[tuple] = None) -> None:
    """Valida se o interpretador Python em execução atende ao piso mínimo (>= 3.10) (#231).

    Emite mensagem com instrução prescritiva de remediação para Rocky Linux 9 e encerra com código 1 se incompatível.
    """
    v = version_info or sys.version_info[:3]
    if v < MIN_PYTHON_VERSION:
        current = f"{v[0]}.{v[1]}.{v[2]}" if len(v) >= 3 else f"{v[0]}.{v[1]}"
        sys.exit(
            f"[ERROR] Python 3.10+ é obrigatório para executar o KSC Runbook (versão ativa: {current}).\n"
            "No Rocky Linux 9 / Enterprise Linux 9, instale o interpretador moderno via AppStream:\n"
            "  sudo dnf install -y python3.11 python3.11-pip\n"
            "E crie/ative um ambiente virtual:\n"
            "  python3.11 -m venv .venv\n"
            "  source .venv/bin/activate\n"
            "Consulte docs/03-pre-requisitos.md para mais detalhes."
        )


def main(argv: Optional[List[str]] = None) -> int:
    """Ponto de entrada do CLI unificado kscctl. Parseia subcomandos e delega para
    as funções específicas de cada operação. Retorna código de saída inteiro."""
    assert_python_version()
    parser = argparse.ArgumentParser(
        prog="python3 -m automation.python.kscctl",
        description="kscctl - Interface de linha de comando unificada para deploy e operações do KSC 16.",
    )
    parser.add_argument(
        "--config",
        dest="config_path",
        default=None,
        help="Caminho para o arquivo .env de configuração.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Ativa saída detalhada (modo verbose).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando: audit
    audit_parser = subparsers.add_parser(
        "audit", help="Auditoria de pré-requisitos ou verificação pós-instalação."
    )
    audit_group = audit_parser.add_mutually_exclusive_group(required=True)
    audit_group.add_argument(
        "--check", action="store_true", help="Executa pré-check (pré-requisitos)."
    )
    audit_group.add_argument(
        "--postcheck", action="store_true", help="Executa pós-check (após instalação)."
    )
    audit_group.add_argument(
        "--report", action="store_true", help="Gera relatório de auditoria consolidado."
    )

    # Subcomando: setup
    setup_parser = subparsers.add_parser(
        "setup", help="Orquestração da instalação local do KSC Server."
    )
    setup_group = setup_parser.add_mutually_exclusive_group(required=True)
    setup_group.add_argument(
        "--check",
        action="store_true",
        help="Valida apenas as variáveis e pré-requisitos locais.",
    )
    setup_group.add_argument(
        "--apply", action="store_true", help="Executa a instalação local completa."
    )

    # Subcomando: db
    db_parser = subparsers.add_parser(
        "db", help="Operações de banco de dados (harden, reset)."
    )
    db_subparsers = db_parser.add_subparsers(dest="subcommand", required=True)

    # db harden
    harden_parser = db_subparsers.add_parser(
        "harden", help="Aplica hardening no PostgreSQL remoto."
    )
    harden_group = harden_parser.add_mutually_exclusive_group(required=True)
    harden_group.add_argument(
        "--check",
        action="store_true",
        help="Compara a configuração de postgresql.conf remota e exibe diff.",
    )
    harden_group.add_argument(
        "--apply", action="store_true", help="Aplica o hardening e reinicia o Postgres."
    )

    # db reset
    reset_parser = db_subparsers.add_parser(
        "reset", help="Exclui e recria os bancos ksc e ksciam."
    )
    reset_group = reset_parser.add_mutually_exclusive_group(required=True)
    reset_group.add_argument(
        "--check", action="store_true", help="Simula o reset dos bancos de dados."
    )
    reset_group.add_argument(
        "--apply", action="store_true", help="Aplica o reset físico dos bancos."
    )
    reset_parser.add_argument(
        "--confirm-token",
        type=str,
        help="Token necessário para confirmação de operação destrutiva.",
    )
    reset_parser.add_argument(
        "--confirm-target",
        type=str,
        help="Alvo esperado (host/FQDN) para validação contextual de segurança.",
    )

    # Subcomando: iam
    iam_parser = subparsers.add_parser(
        "iam", help="Operações de gerenciamento de identidade (MFA)."
    )
    iam_subparsers = iam_parser.add_subparsers(dest="subcommand", required=True)

    # iam purge-mfa
    purge_parser = iam_subparsers.add_parser(
        "purge-mfa",
        help="Limpa chaves/fatores MFA do banco IAM para contornar lockout.",
    )
    purge_group = purge_parser.add_mutually_exclusive_group(required=True)
    purge_group.add_argument(
        "--check", action="store_true", help="Simula a limpeza de tabelas MFA."
    )
    purge_group.add_argument(
        "--apply",
        action="store_true",
        help="Aplica a limpeza física e reinicia os serviços.",
    )
    purge_parser.add_argument(
        "--confirm-token",
        type=str,
        help="Token necessário para confirmação de operação destrutiva.",
    )
    purge_parser.add_argument(
        "--confirm-target",
        type=str,
        help="Alvo esperado (host/FQDN) para validação contextual de segurança.",
    )

    # Subcomando: web
    web_parser = subparsers.add_parser(
        "web", help="Operações de gerenciamento da console web (fix-config)."
    )
    web_subparsers = web_parser.add_subparsers(dest="subcommand", required=True)

    # web fix-config
    fix_web_parser = web_subparsers.add_parser(
        "fix-config", help="Ajusta o config.json do Kaspersky Web Console remoto."
    )
    fix_web_group = fix_web_parser.add_mutually_exclusive_group(required=True)
    fix_web_group.add_argument(
        "--check",
        action="store_true",
        help="Simula correções no config.json do console web.",
    )
    fix_web_group.add_argument(
        "--apply",
        action="store_true",
        help="Aplica correções no config.json e reinicia console.",
    )

    # Subcomando: rollback
    rollback_parser = subparsers.add_parser(
        "rollback",
        help="Remove a instalação do KSC e o estado que ela deixa no host.",
    )
    rollback_group = rollback_parser.add_mutually_exclusive_group(required=True)
    rollback_group.add_argument(
        "--check",
        action="store_true",
        help="Lista o que seria removido, sem alterar o sistema.",
    )
    rollback_group.add_argument(
        "--apply",
        action="store_true",
        help="Executa a remoção. Destrutivo e irreversível.",
    )
    rollback_parser.add_argument(
        "--confirm-token",
        type=str,
        help="Token necessário para confirmação de operação destrutiva.",
    )
    rollback_parser.add_argument(
        "--confirm-target",
        type=str,
        help="Alvo esperado (host/FQDN) para validação contextual de segurança.",
    )
    rollback_parser.add_argument(
        "--verify",
        action="store_true",
        help="Ao final, verifica e reporta resíduos remanescentes.",
    )

    # Subcomando: packages
    packages_parser = subparsers.add_parser(
        "packages",
        help="Gerenciamento e verificação de integridade dos pacotes oficiais Kaspersky.",
    )
    packages_group = packages_parser.add_mutually_exclusive_group(required=True)
    packages_group.add_argument(
        "--list",
        action="store_true",
        help="Lista todos os pacotes oficiais, versões e checksums SHA-256.",
    )
    packages_group.add_argument(
        "--verify-dir",
        type=str,
        metavar="PATH",
        help="Verifica a integridade dos pacotes presentes no diretório informado.",
    )
    packages_group.add_argument(
        "--download",
        type=str,
        metavar="PACKAGE_ID",
        help="Baixa e verifica o checksum SHA-256 do pacote informado.",
    )
    packages_parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Diretório de destino para download (padrão: diretório atual).",
    )

    # Parse arguments
    args = parser.parse_args(argv)

    if args.verbose:
        import logging

        logging.getLogger().setLevel(logging.DEBUG)

    # Execução do subcomando packages (não requer variáveis de ambiente pré-configuradas)
    if args.command == "packages":
        from automation.python import packages

        if args.list:
            packages.print_packages_table()
            return 0
        elif args.verify_dir:
            try:
                res = packages.verify_directory(args.verify_dir)
            except Exception as e:
                print(f"[ERROR] Falha ao verificar diretório: {e}", file=sys.stderr)
                return 1
            print(f"\nVerificação de integridade em: {args.verify_dir}")
            print(f"Pacotes verificados com sucesso: {len(res['verified'])}")
            for item in res["verified"]:
                print(f"  [OK] {item['file']} ({item['product']} {item['version']})")
            if res["failed"]:
                print(f"\n[FALHA] Pacotes com hash divergente: {len(res['failed'])}")
                for item in res["failed"]:
                    print(
                        f"  [CRITICAL] {item['file']} (SHA-256 obtido: {item['actual_sha256']})"
                    )
                return 1
            if res["untracked"]:
                print(f"\nArquivos não rastreados no catálogo: {len(res['untracked'])}")
                for item in res["untracked"]:
                    print(f"  [AVISO] {item['file']}")
            return 0
        elif args.download:
            try:
                final_path = packages.download_package(
                    args.download,
                    target_dir=args.output_dir,
                    verify=True,
                )
                print(f"[SUCCESS] Pacote baixado e validado com sucesso: {final_path}")
                return 0
            except Exception as e:
                print(
                    f"[ERROR] Falha no download/verificação do pacote: {e}",
                    file=sys.stderr,
                )
                return 1

    # Carrega a configuração padrão para comandos operacionais
    from automation.python.config import ConfigError, load_config

    try:
        config = (
            load_config(env_path=args.config_path)
            if args.config_path
            else load_config()
        )
    except ConfigError as e:
        print(f"[ERROR] Configuração inválida: {e}", file=sys.stderr)
        return 2

    # Execução baseada no comando — chama diretamente as funções específicas
    if args.command == "audit":
        from automation.python import ksc_audit

        if args.check:
            return ksc_audit.run_audit_check(config)
        elif args.postcheck:
            return ksc_audit.run_audit_postcheck(config)
        elif args.report:
            return ksc_audit.run_audit_report(config)

    elif args.command == "setup":
        from automation.python import ksc_setup

        if args.check:
            return ksc_setup.run_setup_check(config)
        elif args.apply:
            return ksc_setup.run_setup_apply(config)

    elif args.command == "db" and args.subcommand == "harden":
        from automation.ops.ksc_harden_db import apply_hardening

        apply = args.apply
        try:
            apply_hardening(config, apply=apply)
            return 0
        except Exception as e:
            print(f"[ERROR] Harden falhou: {e}", file=sys.stderr)
            return 1

    elif args.command == "db" and args.subcommand == "reset":
        from automation.ops.reset_ksc_databases import reset_ksc_databases

        if args.apply:
            if not _validate_destructive_confirmation(
                "db reset",
                "RESET-CONFIRM",
                args.confirm_token,
                args.confirm_target,
                config.ksc_host,
            ):
                return 3
            apply = True
        else:
            apply = False
        try:
            reset_ksc_databases(config, apply=apply)
            return 0
        except Exception as e:
            print(f"[ERROR] Reset de bancos falhou: {e}", file=sys.stderr)
            return 1

    elif args.command == "iam" and args.subcommand == "purge-mfa":
        from automation.ops.purge_iam_mfa import purge_iam_mfa

        if args.apply:
            if not _validate_destructive_confirmation(
                "iam purge-mfa",
                "PURGE-CONFIRM",
                args.confirm_token,
                args.confirm_target,
                config.ksc_host,
            ):
                return 3
            apply = True
        else:
            apply = False
        try:
            purge_iam_mfa(config, apply=apply)
            return 0
        except Exception as e:
            print(f"[ERROR] Purge de MFA falhou: {e}", file=sys.stderr)
            return 1

    elif args.command == "rollback":
        from .logging_utils import configure_logger, init_evidence_dir, log_json
        from .rollback import perform_rollback, verify_rollback

        if args.verify and not args.apply:
            print(
                "[ERROR] --verify exige --apply: em modo --check não há o que verificar.",
                file=sys.stderr,
            )
            return 3

        if args.apply:
            if not _validate_destructive_confirmation(
                "rollback",
                "ROLLBACK-CONFIRM",
                args.confirm_token,
                args.confirm_target,
                config.ksc_host,
            ):
                return 3

        evidence_dir = init_evidence_dir("deploy")
        logger = configure_logger(evidence_dir)
        log_json(logger, "rollback_start", apply=bool(args.apply))
        try:
            perform_rollback(config, logger, dry_run=not args.apply)
        except Exception as e:
            log_json(logger, "rollback_failed", error=str(e))
            print(f"[ERROR] Rollback falhou: {e}", file=sys.stderr)
            return 1

        if args.verify and args.apply:
            residuos = verify_rollback(logger, config)
            log_json(logger, "rollback_verify", residuos=len(residuos))
            if residuos:
                print(
                    f"\n[AVISO] {len(residuos)} resíduo(s) remanescente(s):",
                    file=sys.stderr,
                )
                for item in residuos:
                    print(f"  - {item}", file=sys.stderr)
                return 1
            print("\nVerificação: nenhum resíduo do KSC encontrado no host.")

        log_json(logger, "rollback_success")
        return 0

    elif args.command == "web" and args.subcommand == "fix-config":
        from automation.ops import fix_web_console_config

        apply = args.apply
        try:
            fix_web_console_config.fix_web_console_config(config, apply=apply)
            return 0
        except Exception as e:
            print(f"[ERROR] Correção do console web falhou: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
