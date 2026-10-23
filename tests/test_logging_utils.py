# -*- coding: utf-8 -*-
"""Testes unitários dedicados para automation/python/logging_utils.py (Issue #99)."""

import json
import logging
import stat
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from automation.python import logging_utils
from automation.python.logging_utils import (
    configure_logger,
    init_evidence_dir,
    log_json,
)


def test_init_evidence_dir_creates_restricted_hierarchy(tmp_path, monkeypatch):
    """Garante que init_evidence_dir cria evidence/<run_type>/<timestamp> com modo 0700."""
    monkeypatch.chdir(tmp_path)

    evidence_path = init_evidence_dir("precheck")

    assert evidence_path.exists()
    assert evidence_path.is_dir()
    assert evidence_path.parent.name == "precheck"
    assert evidence_path.parent.parent.name == "evidence"

    # Validar permissões 0700 (somente dono tem rwx)
    mode_evidence = stat.S_IMODE(Path("evidence").stat().st_mode)
    mode_run_type = stat.S_IMODE(evidence_path.parent.stat().st_mode)
    mode_target = stat.S_IMODE(evidence_path.stat().st_mode)

    assert mode_evidence == 0o700
    assert mode_run_type == 0o700
    assert mode_target == 0o700


def test_configure_logger_creates_run_log_with_restricted_permissions(tmp_path):
    """Garante que configure_logger cria run.log com modo 0600 e handlers apropriados."""
    logger_name = f"test_{tmp_path.name}"
    # Garante logger limpo
    test_logger = logging.getLogger(f"ksc_{logger_name}")
    test_logger.handlers.clear()

    target_dir = tmp_path / logger_name
    target_dir.mkdir(mode=0o700)

    logger = configure_logger(target_dir)

    log_file = target_dir / "run.log"
    assert log_file.exists()
    assert stat.S_IMODE(log_file.stat().st_mode) == 0o600

    # Verifica handlers: 1 StreamHandler e 1 FileHandler
    stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)]
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    assert len(stream_handlers) == 1
    assert len(file_handlers) == 1

    # Fechar handlers para liberar arquivo
    for h in file_handlers:
        h.close()


def test_configure_logger_is_idempotent_no_duplicate_handlers(tmp_path):
    """Garante que chamadas subsequentes a configure_logger não duplicam handlers."""
    target_dir = tmp_path / "idempotent_test"
    target_dir.mkdir(mode=0o700)

    logger1 = configure_logger(target_dir)
    handler_count_1 = len(logger1.handlers)

    logger2 = configure_logger(target_dir)
    handler_count_2 = len(logger2.handlers)

    assert logger1 is logger2
    assert handler_count_1 == handler_count_2

    for h in logger1.handlers:
        if isinstance(h, logging.FileHandler):
            h.close()


def test_log_json_writes_expected_json_structure(tmp_path):
    """Valida se log_json grava payload JSON com event, timestamp UTC e metadados."""
    mock_logger = MagicMock()

    log_json(mock_logger, "test_event", user="operator1", step=42, status="OK")

    assert mock_logger.info.called
    call_arg = mock_logger.info.call_args[0][0]
    data = json.loads(call_arg)

    assert data["event"] == "test_event"
    assert "timestamp" in data
    assert data["timestamp"].endswith("Z") or data["timestamp"].endswith("+00:00")
    assert data["user"] == "operator1"
    assert data["step"] == 42
    assert data["status"] == "OK"
