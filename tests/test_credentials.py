"""
Testes de propriedade para automation.python.credentials.

Usa Hypothesis para verificar invariantes universais das funções geradoras.
"""
import string

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from automation.python.credentials import (
    generate_password,
    generate_test_db_name,
    generate_username,
)


# Feature: credential-sanitization, Property 1: generate_password retorna comprimento exato
@given(st.integers(min_value=8, max_value=256))
@settings(max_examples=200)
def test_password_length(length):
    """Property 1: generate_password retorna string de comprimento exato.

    Validates: Requirements 1.1
    """
    assert len(generate_password(length)) == length


# Feature: credential-sanitization, Property 2: include_symbols=False retorna apenas alfanuméricos
@given(st.integers(min_value=8, max_value=256))
@settings(max_examples=200)
def test_password_no_symbols(length):
    """Property 2: generate_password com include_symbols=False retorna apenas alfanuméricos.

    Validates: Requirements 1.8
    """
    pwd = generate_password(length, include_symbols=False)
    allowed = set(string.ascii_letters + string.digits)
    assert all(c in allowed for c in pwd)


# Feature: credential-sanitization, Property 3: comprimento inválido lança ValueError
@given(st.one_of(st.integers(max_value=7), st.integers(min_value=257)))
@settings(max_examples=100)
def test_password_invalid_length(length):
    """Property 3: generate_password com comprimento inválido lança ValueError.

    Validates: Requirements 1.9
    """
    with pytest.raises(ValueError, match="length deve estar entre 8 e 256"):
        generate_password(length)


# ---------------------------------------------------------------------------
# Testes de Exemplo — Task 1.4
# Validates: Requirements 1.1, 1.3, 1.4, 1.5
# ---------------------------------------------------------------------------


def test_password_default_length():
    """generate_password() sem argumentos retorna string de 24 caracteres."""
    assert len(generate_password()) == 24


def test_username_default_prefix():
    """generate_username() sem argumentos começa com 'testuser_'."""
    result = generate_username()
    assert result.startswith("testuser_")


def test_db_name_default_prefix():
    """generate_test_db_name() sem argumentos começa com 'ksctest_'."""
    result = generate_test_db_name()
    assert result.startswith("ksctest_")


def test_password_min_length():
    """generate_password(8) retorna string de exatamente 8 caracteres."""
    assert len(generate_password(8)) == 8


def test_password_max_length():
    """generate_password(256) retorna string de exatamente 256 caracteres."""
    assert len(generate_password(256)) == 256


import re

from automation.python.credentials import (
    generate_hostile_password,
    generate_synthetic_fqdn,
    generate_test_db_name,
    generate_username,
)


# Feature: credential-sanitization, Property 4: hostile_password contém todos os 5 conjuntos obrigatórios
@given(st.just(None))
@settings(max_examples=500)
def test_hostile_password_contains_all_sets(_):
    """Property 4: generate_hostile_password sempre contém todos os cinco conjuntos obrigatórios.

    Os cinco conjuntos obrigatórios são: "'", " ", ";", "&", "$(").

    Validates: Requirements 1.2
    """
    pwd = generate_hostile_password()
    assert "'" in pwd, f"Aspas simples ausente em: {pwd!r}"
    assert " " in pwd, f"Espaço ausente em: {pwd!r}"
    assert ";" in pwd, f"Ponto-e-vírgula ausente em: {pwd!r}"
    assert "&" in pwd, f"Ampersand ausente em: {pwd!r}"
    assert "$(" in pwd, f"Sequência '$(' ausente em: {pwd!r}"


# Feature: credential-sanitization, Property 5: generate_synthetic_fqdn sempre respeita o formato ksc-{hex8}.test
@given(st.just(None))
@settings(max_examples=200)
def test_synthetic_fqdn_format(_):
    """Property 5: generate_synthetic_fqdn retorna string no formato ksc-{hex8}.test.

    Validates: Requirements 1.3
    """
    fqdn = generate_synthetic_fqdn()
    assert re.fullmatch(r"ksc-[0-9a-f]{8}\.test", fqdn), (
        f"FQDN fora do formato esperado: {fqdn!r}"
    )


# Feature: credential-sanitization, Property 6: generate_username e generate_test_db_name respeitam seus formatos
@given(
    st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
    )
)
@settings(max_examples=100)
def test_username_and_db_name_format(prefix):
    """Property 6: generate_username e generate_test_db_name respeitam o formato {prefix}_{hex6}.

    Validates: Requirements 1.4, 1.5
    """
    username = generate_username(prefix)
    assert re.fullmatch(rf"{re.escape(prefix)}_[0-9a-f]{{6}}", username), (
        f"generate_username({prefix!r}) retornou formato inválido: {username!r}"
    )

    db_name = generate_test_db_name(prefix)
    assert re.fullmatch(rf"{re.escape(prefix)}_[0-9a-f]{{6}}", db_name), (
        f"generate_test_db_name({prefix!r}) retornou formato inválido: {db_name!r}"
    )


# Feature: credential-sanitization, Property 7: unicidade probabilística das funções geradoras
@given(st.just(None))
@settings(max_examples=1)
def test_uniqueness_generate_password(_):
    """Property 7: generate_password produz >= 999 valores distintos em 1000 chamadas.

    Validates: Requirements 1.6
    """
    results = [generate_password() for _ in range(1000)]
    assert len(set(results)) >= 999, (
        f"generate_password produziu apenas {len(set(results))} valores distintos em 1000 chamadas"
    )


@given(st.just(None))
@settings(max_examples=1)
def test_uniqueness_generate_hostile_password(_):
    """Property 7: generate_hostile_password produz >= 999 valores distintos em 1000 chamadas.

    Validates: Requirements 1.6
    """
    results = [generate_hostile_password() for _ in range(1000)]
    assert len(set(results)) >= 999, (
        f"generate_hostile_password produziu apenas {len(set(results))} valores distintos em 1000 chamadas"
    )


@given(st.just(None))
@settings(max_examples=1)
def test_uniqueness_generate_synthetic_fqdn(_):
    """Property 7: generate_synthetic_fqdn produz >= 999 valores distintos em 1000 chamadas.

    Validates: Requirements 1.6
    """
    results = [generate_synthetic_fqdn() for _ in range(1000)]
    assert len(set(results)) >= 999, (
        f"generate_synthetic_fqdn produziu apenas {len(set(results))} valores distintos em 1000 chamadas"
    )


@given(st.just(None))
@settings(max_examples=1)
def test_uniqueness_generate_username(_):
    """Property 7: generate_username produz >= 999 valores distintos em 1000 chamadas.

    Validates: Requirements 1.6
    """
    results = [generate_username() for _ in range(1000)]
    assert len(set(results)) >= 999, (
        f"generate_username produziu apenas {len(set(results))} valores distintos em 1000 chamadas"
    )


@given(st.just(None))
@settings(max_examples=1)
def test_uniqueness_generate_test_db_name(_):
    """Property 7: generate_test_db_name produz >= 999 valores distintos em 1000 chamadas.

    Validates: Requirements 1.6
    """
    results = [generate_test_db_name() for _ in range(1000)]
    assert len(set(results)) >= 999, (
        f"generate_test_db_name produziu apenas {len(set(results))} valores distintos em 1000 chamadas"
    )
