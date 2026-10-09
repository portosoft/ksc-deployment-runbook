from unittest.mock import patch, MagicMock

from automation.python.ksc_audit import main, ConfigError
from automation.python.checks import CheckResult


@patch("automation.python.ksc_audit.parse_args")
@patch("automation.python.ksc_audit.load_config")
def test_main_config_error(mock_load_config, mock_parse_args):
    mock_load_config.side_effect = ConfigError("Test error")
    mock_parse_args.return_value = MagicMock()

    assert main() == 2


@patch("automation.python.ksc_audit.parse_args")
@patch("automation.python.ksc_audit.load_config")
@patch("automation.python.ksc_audit.init_evidence_dir")
@patch("automation.python.ksc_audit.configure_logger")
@patch("automation.python.ksc_audit.log_json")
@patch("automation.python.ksc_audit.run_precheck")
@patch("automation.python.ksc_audit.print_summary")
def test_main_check_success(mock_print_summary, mock_run_precheck, mock_log_json, mock_configure_logger, mock_init_evidence_dir, mock_load_config, mock_parse_args):
    args = MagicMock()
    args.check = True
    args.postcheck = False
    args.report = False
    mock_parse_args.return_value = args

    result = MagicMock(spec=CheckResult)
    result.has_critical = False
    result.items = []
    mock_run_precheck.return_value = result

    assert main() == 0
    mock_run_precheck.assert_called_once()
    mock_print_summary.assert_called_once_with(result)


@patch("automation.python.ksc_audit.parse_args")
@patch("automation.python.ksc_audit.load_config")
@patch("automation.python.ksc_audit.init_evidence_dir")
@patch("automation.python.ksc_audit.configure_logger")
@patch("automation.python.ksc_audit.log_json")
@patch("automation.python.ksc_audit.run_precheck")
@patch("automation.python.ksc_audit.print_summary")
def test_main_check_critical(mock_print_summary, mock_run_precheck, mock_log_json, mock_configure_logger, mock_init_evidence_dir, mock_load_config, mock_parse_args):
    args = MagicMock()
    args.check = True
    args.postcheck = False
    args.report = False
    mock_parse_args.return_value = args

    result = MagicMock(spec=CheckResult)
    result.has_critical = True
    result.items = []
    mock_run_precheck.return_value = result

    assert main() == 1
    mock_run_precheck.assert_called_once()
    mock_print_summary.assert_called_once_with(result)


@patch("automation.python.ksc_audit.parse_args")
@patch("automation.python.ksc_audit.load_config")
@patch("automation.python.ksc_audit.init_evidence_dir")
@patch("automation.python.ksc_audit.configure_logger")
@patch("automation.python.ksc_audit.log_json")
@patch("automation.python.ksc_audit.run_postcheck")
@patch("automation.python.ksc_audit.print_summary")
def test_main_postcheck_success(mock_print_summary, mock_run_postcheck, mock_log_json, mock_configure_logger, mock_init_evidence_dir, mock_load_config, mock_parse_args):
    args = MagicMock()
    args.check = False
    args.postcheck = True
    args.report = False
    mock_parse_args.return_value = args

    result = MagicMock(spec=CheckResult)
    result.has_critical = False
    result.items = []
    mock_run_postcheck.return_value = result

    assert main() == 0
    mock_run_postcheck.assert_called_once()
    mock_print_summary.assert_called_once_with(result)


@patch("automation.python.ksc_audit.parse_args")
@patch("automation.python.ksc_audit.load_config")
@patch("automation.python.ksc_audit.init_evidence_dir")
@patch("automation.python.ksc_audit.configure_logger")
@patch("automation.python.ksc_audit.log_json")
@patch("automation.python.ksc_audit.run_postcheck")
@patch("automation.python.ksc_audit.print_summary")
def test_main_postcheck_critical(mock_print_summary, mock_run_postcheck, mock_log_json, mock_configure_logger, mock_init_evidence_dir, mock_load_config, mock_parse_args):
    args = MagicMock()
    args.check = False
    args.postcheck = True
    args.report = False
    mock_parse_args.return_value = args

    result = MagicMock(spec=CheckResult)
    result.has_critical = True
    result.items = []
    mock_run_postcheck.return_value = result

    assert main() == 1
    mock_run_postcheck.assert_called_once()
    mock_print_summary.assert_called_once_with(result)


@patch("automation.python.ksc_audit.parse_args")
@patch("automation.python.ksc_audit.load_config")
@patch("automation.python.ksc_audit.init_evidence_dir")
@patch("automation.python.ksc_audit.run_precheck")
@patch("automation.python.ksc_audit.run_postcheck")
@patch("automation.python.ksc_audit.generate_markdown_report")
@patch("automation.python.ksc_audit.convert_markdown_to_pdf")
def test_main_report(mock_convert_pdf, mock_gen_md, mock_run_postcheck, mock_run_precheck, mock_init_evidence_dir, mock_load_config, mock_parse_args):
    args = MagicMock()
    args.check = False
    args.postcheck = False
    args.report = True
    mock_parse_args.return_value = args

    report_dir = MagicMock()
    mock_init_evidence_dir.return_value = report_dir

    mock_pdf_path = MagicMock()
    mock_pdf_path.exists.return_value = True

    mock_md_path = MagicMock()

    def side_effect(arg):
        if arg == "report.md":
            return mock_md_path
        if arg == "report.pdf":
            return mock_pdf_path
        return MagicMock()

    report_dir.__truediv__.side_effect = side_effect

    assert main() == 0
    mock_run_precheck.assert_called_once()
    mock_run_postcheck.assert_called_once()
    mock_gen_md.assert_called_once()
    mock_convert_pdf.assert_called_once()


@patch("automation.python.ksc_audit.parse_args")
@patch("automation.python.ksc_audit.load_config")
def test_main_no_args_matched(mock_load_config, mock_parse_args):
    args = MagicMock()
    args.check = False
    args.postcheck = False
    args.report = False
    mock_parse_args.return_value = args

    assert main() == 2
