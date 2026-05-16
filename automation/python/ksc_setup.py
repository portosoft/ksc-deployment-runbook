#!/usr/bin/env python3
import sys
import argparse
from .config import load_config, ConfigError
from .logging_utils import init_evidence_dir, configure_logger, log_json
from .setup_steps import perform_setup, perform_precheck_only, SetupError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Setup do ambiente para Kaspersky Security Center 16.x"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check",
        action="store_true",
        help="Valida apenas as variáveis e pré-requisitos.",
    )
    group.add_argument(
        "--apply",
        action="store_true",
        help="Executa o deploy completo.",
    )
    return parser.parse_args()


def print_summary(result) -> None:
    print("\n=== RESUMO DOS CHECKS ===")
    for item in result.items:
        print(f"- [{item.status.upper()}] {item.name}: {item.message}")
    if result.has_critical:
        print("\nStatus geral: CRITICAL (há falhas que bloqueiam).")
    else:
        print("\nStatus geral: OK (sem falhas críticas).")


def main():
    args = parse_args()
    try:
        config = load_config()
    except ConfigError as e:
        print(f"[ERROR] Configuração inválida: {e}", file=sys.stderr)
        return 2

    if args.check:
        evidence_dir = init_evidence_dir("precheck")
        logger = configure_logger(evidence_dir)
        log_json(logger, "setup_precheck_start")
        result = perform_precheck_only(config, logger)
        log_json(logger, "setup_precheck_result", has_critical=result.has_critical)
        print_summary(result)
        return 1 if result.has_critical else 0

    if args.apply:
        evidence_dir = init_evidence_dir("deploy")
        logger = configure_logger(evidence_dir)
        log_json(logger, "setup_apply_start")
        try:
            perform_setup(config, logger)
        except SetupError as e:
            log_json(logger, "setup_apply_failed", error=str(e))
            print(f"[ERROR] Falha na instalação: {e}", file=sys.stderr)
            return 2
        log_json(logger, "setup_apply_success")
        print("Instalação concluída com sucesso.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
