# -*- coding: utf-8 -*-
"""
Ferramenta CLI Unificada KSCCTL - Entrypoint Operacional da Portosoft.
Permite executar auditorias locais, instalação e todas as operações remotas
com auditoria e tokens de confirmação para ações destrutivas.
"""

import sys
import argparse
from automation.python.config import load_config, ConfigError
from automation.python.ksc_audit import (
    run_audit_check,
    run_audit_postcheck,
    run_audit_report,
)
from automation.python.ksc_setup import run_setup_check, run_setup_apply

# Importa as operações refatoradas
from automation.ops.ksc_harden_db import apply_hardening
from automation.ops.reset_ksc_databases import reset_ksc_databases
from automation.ops.purge_iam_mfa import purge_iam_mfa
from automation.ops.fix_web_console_config import fix_web_console_config


def main():
    """Ponto de entrada do CLI unificado kscctl. Parseia subcomandos e delega para
    as funções específicas de cada operação. Retorna código de saída inteiro."""
    parser = argparse.ArgumentParser(
        description="kscctl - Interface de linha de comando unificada para deploy e operações do KSC 16."
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

    # Parse arguments
    args = parser.parse_args()

    # Carrega a configuração padrão
    try:
        config = load_config()
    except ConfigError as e:
        print(f"[ERROR] Configuração inválida: {e}", file=sys.stderr)
        return 2

    # Execução baseada no comando — chama diretamente as funções específicas
    if args.command == "audit":
        if args.check:
            return run_audit_check(config)
        elif args.postcheck:
            return run_audit_postcheck(config)
        elif args.report:
            return run_audit_report(config)

    elif args.command == "setup":
        if args.check:
            return run_setup_check(config)
        elif args.apply:
            return run_setup_apply(config)

    elif args.command == "db" and args.subcommand == "harden":
        apply = args.apply
        try:
            apply_hardening(config, apply=apply)
            return 0
        except Exception as e:
            print(f"[ERROR] Harden falhou: {e}", file=sys.stderr)
            return 1

    elif args.command == "db" and args.subcommand == "reset":
        if args.apply:
            if args.confirm_token != "RESET-CONFIRM":
                print(
                    "[ERROR] Token de confirmação ausente ou inválido (--confirm-token=RESET-CONFIRM).",
                    file=sys.stderr,
                )
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
        if args.apply:
            if args.confirm_token != "PURGE-CONFIRM":
                print(
                    "[ERROR] Token de confirmação ausente ou inválido (--confirm-token=PURGE-CONFIRM).",
                    file=sys.stderr,
                )
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

    elif args.command == "web" and args.subcommand == "fix-config":
        apply = args.apply
        try:
            fix_web_console_config(config, apply=apply)
            return 0
        except Exception as e:
            print(f"[ERROR] Correção do console web falhou: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
