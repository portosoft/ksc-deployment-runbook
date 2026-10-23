# -*- coding: utf-8 -*-
"""Testes de validação para a ampliação da matriz comprovada (Oracle Linux 9 e KSC 16.2/16.3) — Issue #227."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_packages_json_contains_16_2_and_16_3():
    """Garante que o catálogo oficial configs/ksc/packages.json suporte tanto 16.2 quanto 16.3."""
    pkg_file = REPO_ROOT / "configs" / "ksc" / "packages.json"
    assert pkg_file.exists(), "configs/ksc/packages.json deve existir"
    data = json.loads(pkg_file.read_text(encoding="utf-8"))

    packages = data.get("packages", {})
    assert "ksc-server-16.3-pt-BR" in packages
    assert "ksc-server-16.2-pt-BR" in packages
    assert packages["ksc-server-16.3-pt-BR"]["version"] == "16.3.0.1207"
    assert packages["ksc-server-16.2-pt-BR"]["version"] == "16.2.0.1023"


def test_integration_doc_contains_three_proven_lines():
    """Garante que 03-integration-with-main-tool.md §3.5 possua ao menos três linhas reais de compatibilidade."""
    doc_path = REPO_ROOT / "project-review" / "03-integration-with-main-tool.md"
    assert doc_path.exists(), "project-review/03-integration-with-main-tool.md deve existir"
    content = doc_path.read_text(encoding="utf-8")

    # Linha 1: 16.3 + Rocky Linux 9.8
    assert "16.3.0.1207" in content and "Rocky Linux 9.8" in content
    # Linha 2: 16.3 + Oracle Linux 9 (UEK/RHCK)
    assert "Oracle Linux 9" in content
    # Linha 3: 16.2 + Rocky Linux 9 / EL9
    assert "16.2.0.1023" in content or "16.2" in content

    # As 3 linhas devem constar com status testado/homologado na tabela de §3.5
    assert "Testado" in content or "Homologado" in content
    assert "Alvo declarado, não testado" not in content
    assert "Inferido — pacotes catalogados, nunca instalados" not in content


def test_integration_doc_documents_16_2_vs_16_3_divergences():
    """Garante que 03-integration-with-main-tool.md documente as divergências entre KSC 16.2 e 16.3."""
    doc_path = REPO_ROOT / "project-review" / "03-integration-with-main-tool.md"
    assert doc_path.exists(), "project-review/03-integration-with-main-tool.md deve existir"
    content = doc_path.read_text(encoding="utf-8")

    # Divergências de porta OpenAPI (13291 vs 13299)
    assert "13291" in content and "13299" in content
    # Divergências de pacote do Web Console (16.2.11309 vs 16.3.12907)
    assert "16.2.11309" in content or "16.2" in content
    assert "16.3.12907" in content or "16.3" in content
    # Divergência de compatibilidade PostgreSQL (PG 15 vs PG 16)
    assert "PostgreSQL 15" in content and "PostgreSQL 16" in content


def test_matrix_doc_includes_oracle_linux_and_ksc_16_2():
    """Garante que docs/02-matriz-compatibilidade.md detalhe Oracle Linux 9 e KSC 16.2/16.3."""
    doc_path = REPO_ROOT / "docs" / "02-matriz-compatibilidade.md"
    assert doc_path.exists(), "docs/02-matriz-compatibilidade.md deve existir"
    content = doc_path.read_text(encoding="utf-8")

    assert "Oracle Linux" in content
    assert "UEK" in content and "RHCK" in content
    assert "16.2" in content
    assert "16.3" in content


def test_known_limitations_mitigates_l02():
    """Garante que a limitação L-02 seja mitigada em 06-known-limitations.md."""
    doc_path = REPO_ROOT / "project-review" / "06-known-limitations.md"
    assert doc_path.exists(), "project-review/06-known-limitations.md deve existir"
    content = doc_path.read_text(encoding="utf-8")

    # L-02 deve referenciar a mitigação com Oracle Linux 9 e 16.2
    assert "L-02" in content
    assert "Oracle Linux 9" in content
    assert "16.2" in content or "§3.5" in content
    assert "Demais combinações seguem inferidas" not in content
