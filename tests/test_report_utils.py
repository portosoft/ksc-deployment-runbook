import os
import stat
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from automation.python.checks import CheckItem, CheckResult
from automation.python.report_utils import (
    convert_markdown_to_pdf,
    generate_markdown_report,
)


def test_generate_markdown_report(tmp_path):
    precheck = CheckResult(
        items=[CheckItem(name="ram", status="ok", message="RAM is sufficient")]
    )
    postcheck = CheckResult(
        items=[CheckItem(name="db", status="critical", message="DB is down")]
    )

    evidence_root = Path("/fake/evidence/root")
    output_path = tmp_path / "report.md"

    generate_markdown_report(precheck, postcheck, evidence_root, output_path)

    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    # Check headers
    assert "# Relatório de Auditoria KSC 16.x" in content
    assert "## Pré-check" in content
    assert "## Pós-check" in content
    assert "## Evidências" in content

    # Check precheck items
    assert "- **ram** [OK]: RAM is sufficient" in content

    # Check postcheck items
    assert "- **db** [CRITICAL]: DB is down" in content

    # Check evidence path
    assert "`/fake/evidence/root`" in content

    # Verify secure file permissions on POSIX platforms.
    if sys.platform != "win32":
        actual_mode = stat.S_IMODE(os.stat(str(output_path)).st_mode)
        assert actual_mode == 0o600


@patch("automation.python.report_utils._load_md2pdf")
def test_convert_markdown_to_pdf_success(mock_load_md2pdf, tmp_path):
    md_path = tmp_path / "in.md"
    pdf_path = tmp_path / "out.pdf"
    mock_md2pdf = MagicMock()
    mock_load_md2pdf.return_value = mock_md2pdf

    convert_markdown_to_pdf(md_path, pdf_path)

    # md2pdf 3.x: md2pdf(pdf, raw=None, md=None, ...). O parâmetro md_file_path
    # é da linha 1.x e fazia a conversão sempre lançar TypeError.
    mock_md2pdf.assert_called_once_with(pdf_path, md=md_path)


@patch("logging.getLogger")
@patch("automation.python.report_utils._load_md2pdf")
def test_convert_markdown_to_pdf_failure(mock_load_md2pdf, mock_get_logger, tmp_path):
    mock_load_md2pdf.side_effect = Exception("Test failure")
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    md_path = tmp_path / "in.md"
    pdf_path = tmp_path / "out.pdf"

    convert_markdown_to_pdf(md_path, pdf_path)

    mock_get_logger.assert_called_once_with("automation.python.report_utils")
    mock_logger.warning.assert_called_once()
    assert (
        "Não foi possível gerar o PDF: Test failure"
        in mock_logger.warning.call_args[0][0]
    )


def test_convert_markdown_to_pdf_uses_current_md2pdf_signature(tmp_path, monkeypatch):
    """A assinatura do md2pdf 3.x é md2pdf(pdf, raw=None, md=None, ...).

    A chamada usava `md_file_path`, parâmetro da linha 1.x: a conversão sempre
    lançava TypeError, capturado e registrado apenas como warning, de modo que
    o PDF de evidências nunca era gerado.
    """
    from pathlib import Path

    from automation.python import report_utils

    recebido = {}

    def fake_md2pdf(pdf, raw=None, md=None, **kwargs):
        recebido["pdf"] = pdf
        recebido["md"] = md
        Path(pdf).write_bytes(b"%PDF-1.7\n")

    monkeypatch.setattr(report_utils, "_load_md2pdf", lambda: fake_md2pdf)

    markdown = tmp_path / "report.md"
    markdown.write_text("# Relatorio\n")
    pdf = tmp_path / "report.pdf"

    report_utils.convert_markdown_to_pdf(markdown, pdf)

    assert recebido["md"] == markdown
    assert recebido["pdf"] == pdf
    assert pdf.exists()


def test_report_omits_precheck_when_ksc_already_installed(tmp_path):
    """Reexecutar o pré-check pós-deploy marcava como crítico as portas do próprio KSC."""
    from pathlib import Path

    from automation.python.checks import CheckItem, CheckResult
    from automation.python.report_utils import generate_markdown_report

    post = CheckResult(items=[CheckItem(name="web_console", status="ok", message="LISTEN")])
    destino = tmp_path / "report.md"

    generate_markdown_report(None, post, Path("evidence"), destino)

    conteudo = destino.read_text()
    assert "Não aplicável" in conteudo
    assert "CRITICAL" not in conteudo
    assert "Nenhuma falha crítica no pós-check." in conteudo


def test_report_summarises_critical_failures(tmp_path):
    from pathlib import Path

    from automation.python.checks import CheckItem, CheckResult
    from automation.python.report_utils import generate_markdown_report

    post = CheckResult(
        items=[
            CheckItem(name="postgresql", status="critical", message="Inativo."),
            CheckItem(name="selinux", status="ok", message="enforcing"),
        ]
    )
    destino = tmp_path / "report.md"

    generate_markdown_report(None, post, Path("evidence"), destino)

    conteudo = destino.read_text()
    assert "1 falha(s) crítica(s)" in conteudo
    assert "postgresql" in conteudo
