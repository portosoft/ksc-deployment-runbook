from pathlib import Path
from .checks import CheckResult
from automation.python.utils.secure_file import write_secure_file


def generate_markdown_report(
    precheck_result: CheckResult,
    postcheck_result: CheckResult,
    evidence_root: Path,
    output_path: Path,
) -> None:
    """Gera relatório Markdown a partir dos resultados de check.

    O relatório inclui seções de pré-check e pós-check com status e mensagens,
    além do caminho para as evidências brutas.

    Args:
        precheck_result: Resultado dos checks de pré-instalação.
        postcheck_result: Resultado dos checks pós-instalação.
        evidence_root: Diretório raiz onde as evidências foram salvas.
        output_path: Caminho do arquivo Markdown de saída.
    """
    content = "# Relatório de Auditoria KSC 16.x\n\n"

    content += "## Pré-check\n"
    for item in precheck_result.items:
        content += f"- **{item.name}** [{item.status.upper()}]: {item.message}\n"

    content += "\n## Pós-check\n"
    for item in postcheck_result.items:
        content += f"- **{item.name}** [{item.status.upper()}]: {item.message}\n"

    content += f"\n## Evidências\n"
    content += f"Todos os logs e evidências brutos podem ser encontrados em: `{evidence_root}`\n"

    write_secure_file(str(output_path), content, mode=0o600)


def convert_markdown_to_pdf(markdown_path: Path, pdf_path: Path) -> None:
    """Converte o relatório Markdown para PDF via md2pdf. Loga warning em caso de falha.

    Args:
        markdown_path: Caminho do arquivo Markdown de entrada.
        pdf_path: Caminho do arquivo PDF de saída.
    """
    try:
        from md2pdf.core import md2pdf

        md2pdf(pdf_path, md_file_path=str(markdown_path))
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Não foi possível gerar o PDF: {e}")
