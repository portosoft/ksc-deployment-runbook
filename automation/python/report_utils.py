from pathlib import Path
from .checks import CheckResult


def generate_markdown_report(
    precheck_result: CheckResult,
    postcheck_result: CheckResult,
    evidence_root: Path,
    output_path: Path,
) -> None:
    content = "# Relatório de Auditoria KSC 16.x\n\n"

    content += "## Pré-check\n"
    for item in precheck_result.items:
        content += f"- **{item.name}** [{item.status.upper()}]: {item.message}\n"

    content += "\n## Pós-check\n"
    for item in postcheck_result.items:
        content += f"- **{item.name}** [{item.status.upper()}]: {item.message}\n"

    content += f"\n## Evidências\n"
    content += f"Todos os logs e evidências brutos podem ser encontrados em: `{evidence_root}`\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def convert_markdown_to_pdf(markdown_path: Path, pdf_path: Path) -> None:
    try:
        from md2pdf.core import md2pdf

        md2pdf(pdf_path, md_file_path=str(markdown_path))
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Não foi possível gerar o PDF: {e}")
