#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

from .config import load_config, ConfigError
from .logging_utils import init_evidence_dir, configure_logger, log_json
from .checks import run_precheck, run_postcheck, CheckResult
from .report_utils import generate_markdown_report, convert_markdown_to_pdf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Auditoria do ambiente para Kaspersky Security Center 16.x"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check",
        action="store_true",
        help="Executa pré-check (pré-requisitos antes da instalação).",
    )
    group.add_argument(
        "--postcheck",
        action="store_true",
        help="Executa pós-check (após instalação do KSC).",
    )
    group.add_argument(
        "--report",
        action="store_true",
        help="Gera relatório consolidado a partir das evidências.",
    )
    return parser.parse_args()


def print_summary(result: CheckResult) -> None:
    print("\n=== RESUMO DOS CHECKS ===")
    for item in result.items:
        print(f"- [{item.status.upper()}] {item.name}: {item.message}")
    if result.has_critical:
        print("\nStatus geral: CRITICAL (há falhas que bloqueiam).")
    else:
        print("\nStatus geral: OK (sem falhas críticas).")


def main() -> int:
    args = parse_args()

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"[ERROR] Configuração inválida: {exc}", file=sys.stderr)
        return 2

    if args.check:
        evidence_dir = init_evidence_dir("precheck")
        logger = configure_logger(evidence_dir)
        log_json(logger, "precheck_start")

        result = run_precheck(config)
        log_json(
            logger,
            "precheck_result",
            has_critical=result.has_critical,
            total_items=len(result.items),
        )

        print_summary(result)
        return 1 if result.has_critical else 0

    if args.postcheck:
        evidence_dir = init_evidence_dir("postcheck")
        logger = configure_logger(evidence_dir)
        log_json(logger, "postcheck_start")

        result = run_postcheck(config)
        log_json(
            logger,
            "postcheck_result",
            has_critical=result.has_critical,
            total_items=len(result.items),
        )

        print_summary(result)
        return 1 if result.has_critical else 0

    if args.report:
        evidence_root = Path("evidence")

        # Para gerar o report dinâmico, rodamos os checks em modo leve
        # Na prática, isso poderia ler logs de `evidence_root`.
        print("Coletando estado atual para relatório...")
        pre = run_precheck(config)
        post = run_postcheck(config)

        report_dir = init_evidence_dir("reports")
        md_path = report_dir / "report.md"
        pdf_path = report_dir / "report.pdf"

        generate_markdown_report(pre, post, evidence_root, md_path)
        print(f"Relatório Markdown gerado em {md_path}")

        print("Gerando PDF...")
        convert_markdown_to_pdf(md_path, pdf_path)
        if pdf_path.exists():
            print(f"Relatório PDF gerado em {pdf_path}")

        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
