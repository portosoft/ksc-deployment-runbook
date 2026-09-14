from importlib import import_module
from pathlib import Path
from typing import Optional

from automation.python.utils.secure_file import write_secure_file

from .checks import CheckResult


def generate_markdown_report(
    precheck_result: Optional[CheckResult],
    postcheck_result: CheckResult,
    evidence_root: Path,
    output_path: Path,
) -> None:
    """Gera relatório Markdown a partir dos resultados de check.

    O relatório inclui seções de pré-check e pós-check com status e mensagens,
    além do caminho para as evidências brutas.

    Args:
        precheck_result: Resultado dos checks de pré-instalação, ou None quando
            o KSC já está instalado e a verificação deixou de ser aplicável.
        postcheck_result: Resultado dos checks pós-instalação.
        evidence_root: Diretório raiz onde as evidências foram salvas.
        output_path: Caminho do arquivo Markdown de saída.
    """
    content = "# Relatório de Auditoria KSC 16.x\n\n"

    content += "## Pré-check\n"
    if precheck_result is None:
        # O pré-check valida condições de partida — entre elas, portas livres.
        # Reexecutá-lo em um servidor já instalado marcaria como crítico
        # justamente as portas que o KSC passou a ocupar corretamente.
        content += (
            "Não aplicável: o KSC já está instalado neste servidor. As verificações "
            "de pré-instalação avaliam condições de partida, como portas livres, "
            "que deixam de valer depois do deploy.\n"
        )
    else:
        for item in precheck_result.items:
            content += f"- **{item.name}** [{item.status.upper()}]: {item.message}\n"

    content += "\n## Pós-check\n"
    for item in postcheck_result.items:
        content += f"- **{item.name}** [{item.status.upper()}]: {item.message}\n"

    criticos = [i for i in postcheck_result.items if i.status == "critical"]
    content += "\n## Resumo\n"
    if criticos:
        content += f"**{len(criticos)} falha(s) crítica(s)** no pós-check: "
        content += ", ".join(i.name for i in criticos) + "\n"
    else:
        content += "Nenhuma falha crítica no pós-check.\n"

    content += f"\n## Evidências\n"
    content += f"Todos os logs e evidências brutos podem ser encontrados em: `{evidence_root.as_posix()}`\n"

    write_secure_file(str(output_path), content, mode=0o600)


def _load_md2pdf():
    """Carrega a função md2pdf de forma tardia para facilitar testes e tolerar dependências opcionais."""
    return import_module("md2pdf.core").md2pdf


def convert_markdown_to_pdf(markdown_path: Path, pdf_path: Path) -> None:
    """Converte o relatório Markdown para PDF via md2pdf. Loga warning em caso de falha.

    Args:
        markdown_path: Caminho do arquivo Markdown de entrada.
        pdf_path: Caminho do arquivo PDF de saída.
    """
    try:
        md2pdf = _load_md2pdf()
        # A assinatura do md2pdf 3.x é md2pdf(pdf, raw=None, md=None, ...). O
        # parâmetro `md_file_path` é da linha 1.x e fazia a conversão falhar
        # silenciosamente com TypeError, registrado apenas como warning.
        md2pdf(Path(pdf_path), md=Path(markdown_path))
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Não foi possível gerar o PDF: {e}")
