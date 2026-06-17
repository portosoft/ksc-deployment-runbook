import os
import stat
from pathlib import Path
from unittest.mock import patch, MagicMock


from automation.python.report_utils import generate_markdown_report, convert_markdown_to_pdf
from automation.python.checks import CheckResult, CheckItem


def test_generate_markdown_report(tmp_path):
    precheck = CheckResult(items=[CheckItem(name="ram", status="ok", message="RAM is sufficient")])
    postcheck = CheckResult(items=[CheckItem(name="db", status="critical", message="DB is down")])

    evidence_root = Path("/fake/evidence/root")
    output_path = tmp_path / "report.md"

    generate_markdown_report(precheck, postcheck, evidence_root, output_path)

    assert output_path.exists()

    content = output_path.read_text()

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

    # Verify secure file permissions
    actual_mode = stat.S_IMODE(os.stat(str(output_path)).st_mode)
    assert actual_mode == 0o600


@patch("automation.python.report_utils.Path")
@patch("md2pdf.core.md2pdf")
def test_convert_markdown_to_pdf_success(mock_md2pdf, mock_path, tmp_path):
    md_path = tmp_path / "in.md"
    pdf_path = tmp_path / "out.pdf"

    convert_markdown_to_pdf(md_path, pdf_path)

    mock_md2pdf.assert_called_once_with(pdf_path, md_file_path=str(md_path))


@patch("logging.getLogger")
@patch("md2pdf.core.md2pdf")
def test_convert_markdown_to_pdf_failure(mock_md2pdf, mock_get_logger, tmp_path):
    mock_md2pdf.side_effect = Exception("Test failure")
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    md_path = tmp_path / "in.md"
    pdf_path = tmp_path / "out.pdf"

    convert_markdown_to_pdf(md_path, pdf_path)

    mock_get_logger.assert_called_once_with("automation.python.report_utils")
    mock_logger.warning.assert_called_once()
    assert "Não foi possível gerar o PDF: Test failure" in mock_logger.warning.call_args[0][0]
