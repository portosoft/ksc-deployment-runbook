# Feature: credential-sanitization, Property 10: make_check_item e make_critical_result preservam os parâmetros fornecidos

"""
Property-based tests for factory functions in tests/factories.py and
KscConfig validation in automation/python/config.py.

Validates: Requirements 3.1, 3.3, 6.1, 6.2
"""

import re
import sys
import os

# Ensure automation module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from factories import make_check_item, make_critical_result
from automation.python.config import KscConfig

VALID_SSLMODES = {"disable", "prefer", "require", "verify-ca", "verify-full"}


def _is_valid_fqdn(s: str) -> bool:
    fqdn_regex = r"(?i)^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$|^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return bool(re.match(fqdn_regex, s))


# Feature: credential-sanitization, Property 10: make_check_item e make_critical_result preservam os parâmetros fornecidos
@given(st.text(), st.text(), st.text())
@settings(max_examples=200)
def test_make_check_item_preserves_params(name, status, message):
    """Validates: Requirements 3.1

    For any strings name, status, and message, make_check_item must return a
    CheckItem whose .name, .status, and .message exactly match the supplied arguments.
    """
    item = make_check_item(name, status, message)
    assert item.name == name
    assert item.status == status
    assert item.message == message


@given(st.text(), st.text())
@settings(max_examples=200)
def test_make_critical_result_preserves_params(name, message):
    """Validates: Requirements 3.3

    For any strings name and message, make_critical_result must return a CheckResult
    containing exactly one item where .name == name, .status == "critical", and
    .message == message.
    """
    result = make_critical_result(name, message)
    assert len(result.items) == 1
    item = result.items[0]
    assert item.name == name
    assert item.status == "critical"
    assert item.message == message


# Feature: credential-sanitization, Property 8: FQDN inválido sempre rejeitado
@given(st.text().filter(lambda s: not _is_valid_fqdn(s)))
@settings(max_examples=100)
def test_invalid_fqdn_rejected(invalid_fqdn):
    """Validates: Requirements 6.1

    For any string that is not a valid hostname, FQDN, or IPv4 address,
    constructing KscConfig with that value as ksc_fqdn must raise ValidationError or ValueError.
    """
    with pytest.raises((ValidationError, ValueError)):
        KscConfig(db_password="x" * 8, ksc_admin_password="x" * 8, ksc_fqdn=invalid_fqdn)


# Feature: credential-sanitization, Property 9: db_sslmode fora do conjunto sempre rejeitado
@given(st.text().filter(lambda s: s not in VALID_SSLMODES))
@settings(max_examples=100)
def test_invalid_sslmode_rejected(invalid_mode):
    """Validates: Requirements 6.2

    For any string not in the allowed SSL mode set, constructing KscConfig
    with that value as db_sslmode must raise ValidationError or ValueError.
    """
    with pytest.raises((ValidationError, ValueError)):
        KscConfig(db_password="x" * 8, ksc_admin_password="x" * 8, db_sslmode=invalid_mode)
