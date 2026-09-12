# -*- coding: utf-8 -*-
"""
Ferramenta CLI Unificada KSCCTL - Entrypoint Operacional do KSC Runbook.
Permite executar auditorias locais, instalação e todas as operações remotas
com auditoria e tokens de confirmação para ações destrutivas.
"""

import argparse
import sys


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
    args = parser.parse_args()

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
        config = load_config()
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
        from automation.ops.purge_iam_mfa import purge_iam_mfa

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
