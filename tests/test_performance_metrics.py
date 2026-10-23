# -*- coding: utf-8 -*-
"""Testes de validação para publicação de métricas de desempenho e QA (Issue #225)."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_performance_metrics_doc_exists_and_contains_data():
    """Garante que docs/15-metricas-desempenho.md documente ambiente, tempos, recursos e sucesso."""
    doc_path = REPO_ROOT / "docs" / "15-metricas-desempenho.md"
    assert doc_path.exists(), "docs/15-metricas-desempenho.md deve existir"
    content = doc_path.read_text(encoding="utf-8")

    # Ambiente
    assert "Rocky Linux 9.8" in content
    assert "16.3.0.1207" in content
    assert "PostgreSQL 16" in content
    assert "Proxmox" in content

    # Tempos medidos
    assert "93" in content or "1m33s" in content or "1 min e 33" in content
    assert "14" in content or "idempotência" in content.lower()

    # Consumo de recursos
    assert "CPU" in content
    assert "RAM" in content or "Memória" in content
    assert "Disco" in content or "Armazenamento" in content

    # Taxa de sucesso
    assert "100%" in content
    assert "Taxa de Sucesso" in content or "taxa de sucesso" in content.lower()


def test_index_doc_includes_performance_metrics():
    """Garante que docs/00-index.md referencie docs/15-metricas-desempenho.md."""
    index_path = REPO_ROOT / "docs" / "00-index.md"
    assert index_path.exists(), "docs/00-index.md deve existir"
    content = index_path.read_text(encoding="utf-8")

    assert "15-metricas-desempenho.md" in content


def test_evidence_metrics_json_and_readme_integrity():
    """Garante que evidence/e2e-225/ possua README e metrics.json válido."""
    evidence_dir = REPO_ROOT / "evidence" / "e2e-225"
    readme_path = evidence_dir / "README.md"
    metrics_path = evidence_dir / "metrics.json"

    assert readme_path.exists(), "evidence/e2e-225/README.md deve existir"
    assert metrics_path.exists(), "evidence/e2e-225/metrics.json deve existir"

    data = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert "environment" in data
    assert "deployment_metrics" in data
    assert "resource_usage" in data
    assert "success_rate" in data

    assert data["environment"]["ksc_version"] == "16.3.0.1207"
    assert data["success_rate"]["rate_percentage"] == 100.0


def test_technical_overview_replaces_hypotheses_with_metrics():
    """Garante que 01-technical-overview.md atualize hipóteses de desempenho por números reais."""
    overview_path = REPO_ROOT / "project-review" / "01-technical-overview.md"
    assert overview_path.exists(), "project-review/01-technical-overview.md deve existir"
    content = overview_path.read_text(encoding="utf-8")

    # Não deve mais classificar desempenho como não comprovado ou não validado
    assert "Qualquer característica de desempenho — [#225]" not in content
    assert "93" in content or "1m33s" in content or "1 min e 33" in content
    assert "15-metricas-desempenho.md" in content or "docs/15" in content


def test_known_limitations_mitigates_l09():
    """Garante que a limitação L-09 seja mitigada em 06-known-limitations.md."""
    limitations_path = REPO_ROOT / "project-review" / "06-known-limitations.md"
    assert limitations_path.exists(), "project-review/06-known-limitations.md deve existir"
    content = limitations_path.read_text(encoding="utf-8")

    # L-09 deve apontar para as métricas consolidadas
    assert "15-metricas-desempenho.md" in content or "docs/15" in content or "e2e-225" in content
