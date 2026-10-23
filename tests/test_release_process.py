# -*- coding: utf-8 -*-
"""Testes de validação para o processo de release, SemVer, matriz de compatibilidade e empacotamento."""

import hashlib
from pathlib import Path
import subprocess
import sys
import tarfile
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_versioning_doc_contains_semver_and_signing_process():
    """Garante que VERSIONING.md defina SemVer, fluxo de branches, assinatura e integridade."""
    versioning_file = REPO_ROOT / "VERSIONING.md"
    assert versioning_file.exists(), "VERSIONING.md deve existir"
    content = versioning_file.read_text(encoding="utf-8")

    assert len(content.splitlines()) >= 30, "VERSIONING.md deve ser um guia detalhado e estruturado"
    assert "Semantic Versioning" in content or "SemVer" in content
    assert "MAJOR" in content and "MINOR" in content and "PATCH" in content
    assert "develop" in content and "main" in content
    assert "SHA256SUMS" in content
    assert "ssh-keygen -Y sign" in content or "ssh-keygen" in content
    assert "ssh-keygen -Y verify" in content or "verify" in content
    assert "Matriz de Compatibilidade" in content or "comprovada" in content


def test_compatibility_matrix_separates_proven_from_declared():
    """Garante que docs/02-matriz-compatibilidade.md separe ambientes comprovados de declarados."""
    matrix_file = REPO_ROOT / "docs" / "02-matriz-compatibilidade.md"
    assert matrix_file.exists(), "docs/02-matriz-compatibilidade.md deve existir"
    content = matrix_file.read_text(encoding="utf-8")

    # Deve separar expressamente ambientes comprovados em execução real de declarados em documentação
    assert "Comprovado em Execução Real" in content or "Ambientes Comprovados" in content
    assert "Declarado em Documentação" in content or "Ambientes Declarados" in content
    assert "Rocky Linux 9.8" in content or "Rocky Linux 9" in content
    assert "16.3.0.1207" in content
    assert "PostgreSQL 16" in content
    assert "Python 3.11" in content
    assert "evidence/e2e-209" in content or "#209" in content
    assert "Oracle Linux" in content
    assert "#227" in content


def test_contributing_references_release_process():
    """Garante que CONTRIBUTING.md referencie o processo de release e VERSIONING.md."""
    contributing_file = REPO_ROOT / "CONTRIBUTING.md"
    assert contributing_file.exists(), "CONTRIBUTING.md deve existir"
    content = contributing_file.read_text(encoding="utf-8")

    assert "VERSIONING.md" in content
    assert "Release" in content or "release" in content


def test_changelog_declares_proven_matrix_and_keepachangelog():
    """Garante que CHANGELOG.md siga Keep a Changelog e declare a matriz comprovada."""
    changelog_file = REPO_ROOT / "CHANGELOG.md"
    assert changelog_file.exists(), "CHANGELOG.md deve existir"
    content = changelog_file.read_text(encoding="utf-8")

    assert "[Unreleased]" in content
    assert "Keep a Changelog" in content
    assert "Ambiente comprovado" in content or "comprovado" in content.lower()


def test_package_release_script_packaging_and_checksum(tmp_path):
    """Garante que scripts/package_release.py empacote o repositório e gere SHA256SUMS."""
    script_path = REPO_ROOT / "scripts" / "package_release.py"
    assert script_path.exists(), "scripts/package_release.py deve existir"

    out_dir = tmp_path / "dist"
    version = "v2.1.0"

    cmd = [
        sys.executable,
        str(script_path),
        "--version",
        version,
        "--output-dir",
        str(out_dir),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    assert res.returncode == 0, f"Falha no script de empacotamento: {res.stderr}\n{res.stdout}"

    tar_file = out_dir / f"ksc-deployment-runbook-{version}.tar.gz"
    sums_file = out_dir / "SHA256SUMS"

    assert tar_file.exists(), f"Arquivo {tar_file} não foi gerado"
    assert sums_file.exists(), f"Arquivo {sums_file} não foi gerado"

    # Verificar que o hash SHA256 do tar.gz confere com SHA256SUMS
    sha256 = hashlib.sha256(tar_file.read_bytes()).hexdigest()
    sums_content = sums_file.read_text(encoding="utf-8")
    assert f"{sha256}  ksc-deployment-runbook-{version}.tar.gz" in sums_content

    # Verificar conteúdo do tarball para garantir limpeza
    with tarfile.open(tar_file, "r:gz") as tar:
        members = tar.getnames()
        # Deve conter componentes principais
        assert any("automation" in m for m in members), "automation deve estar presente no tarball"
        assert any("docs" in m for m in members), "docs deve estar presente no tarball"
        assert any("requirements.txt" in m for m in members), "requirements.txt deve estar no tarball"
        assert any("README.md" in m for m in members), "README.md deve estar no tarball"
        assert any("VERSIONING.md" in m for m in members), "VERSIONING.md deve estar no tarball"

        # NÃO deve conter arquivos indesejados ou sensíveis
        for m in members:
            assert not m.startswith(".git/"), f"Arquivo .git não deve constar no tarball: {m}"
            assert "__pycache__" not in m, f"__pycache__ não deve constar no tarball: {m}"
            assert ".secrets.baseline" not in m, f".secrets.baseline não deve constar no tarball: {m}"
            assert not m.startswith("tests/"), f"tests não deve constar no pacote de distribuição: {m}"
            assert not m.startswith("evidence/"), f"evidence não deve constar no pacote de distribuição: {m}"
            assert not m.startswith(".venv/"), f".venv não deve constar no pacote de distribuição: {m}"


def test_package_release_extracts_changelog_notes():
    """Garante que a função de extração de notas do CHANGELOG.md funcione corretamente."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import package_release  # type: ignore

    changelog_path = REPO_ROOT / "CHANGELOG.md"
    notes = package_release.extract_changelog_notes("2.0.0", changelog_path)
    assert notes, "Notas para 2.0.0 não devem estar vazias"
    assert "Primeira versão com deploy real validado" in notes


def test_release_workflow_configuration():
    """Garante que o workflow .github/workflows/release.yml esteja configurado corretamente."""
    release_workflow = REPO_ROOT / ".github" / "workflows" / "release.yml"
    assert release_workflow.exists(), ".github/workflows/release.yml deve existir"

    content = release_workflow.read_text(encoding="utf-8")
    parsed = yaml.safe_load(content)

    triggers = parsed.get("on") if "on" in parsed else parsed.get(True, {})
    assert "push" in triggers or "workflow_dispatch" in triggers, "Workflow deve ter gatilhos push ou workflow_dispatch"
    if "push" in triggers:
        tags = triggers["push"].get("tags", [])
        assert any("v*" in t for t in tags), "Trigger push deve filtrar tags 'v*'"

    jobs = parsed.get("jobs", {})
    assert "release" in jobs, "Workflow deve conter job 'release'"

    release_job = jobs["release"]
    permissions = release_job.get("permissions", {})
    assert permissions.get("contents") == "write", "Job de release deve ter contents: write para publicar artefatos"
