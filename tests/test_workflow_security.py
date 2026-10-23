# -*- coding: utf-8 -*-
"""Testes de invariantes de segurança e governança para workflows do GitHub Actions.

Garante que:
1. O scanner Aikido não use 'continue-on-error: true' para suprimir alertas de segurança.
2. O workflow de CI não silencie falhas do detect-secrets com '|| true' nem tente auto-commits.
3. Nenhum workflow execute criação de PRs direcionados diretamente para main sem release.
"""

from pathlib import Path
import yaml

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / ".github" / "workflows"


def test_aikido_workflow_does_not_ignore_errors():
    """Garante que o scan do Aikido seja um gate rígido e não use continue-on-error: true."""
    aikido_file = WORKFLOWS_DIR / "aikido.yml"
    assert aikido_file.exists(), "Workflow aikido.yml deve existir"
    content = aikido_file.read_text(encoding="utf-8")
    parsed = yaml.safe_load(content)

    for job_name, job in parsed.get("jobs", {}).items():
        for step in job.get("steps", []):
            assert not step.get("continue-on-error", False), (
                f"O passo '{step.get('name')}' no job '{job_name}' do aikido.yml "
                "não deve possuir 'continue-on-error: true'."
            )


def test_ci_workflow_does_not_mask_secrets_or_auto_commit():
    """Garante que detect-secrets falhe em caso de novos segredos e o CI não faça auto-commit."""
    ci_file = WORKFLOWS_DIR / "ci.yml"
    assert ci_file.exists(), "Workflow ci.yml deve existir"
    content = ci_file.read_text(encoding="utf-8")

    # detect-secrets não deve suprimir erros com '|| true'
    assert "detect-secrets scan" in content
    assert "|| true" not in content, (
        "O CI não deve utilizar '|| true' após detect-secrets scan para suprimir falhas de segredos."
    )

    # Não deve existir step de auto-commit com git push
    parsed = yaml.safe_load(content)
    for job_name, job in parsed.get("jobs", {}).items():
        for step in job.get("steps", []):
            step_name = step.get("name", "").lower()
            assert "auto-commit" not in step_name, (
                f"O passo '{step.get('name')}' em ci.yml não deve executar auto-commits."
            )
            run_cmd = step.get("run", "")
            assert "git push origin" not in run_cmd, (
                f"O passo '{step.get('name')}' não deve realizar 'git push origin' a partir do CI."
            )


def test_recreate_prs_workflow_is_disabled_or_deprecated():
    """Garante que o workflow recreate-prs.yml não possua gatilhos ativos e não crie PRs para main."""
    recreate_file = WORKFLOWS_DIR / "recreate-prs.yml"
    if not recreate_file.exists():
        return

    content = recreate_file.read_text(encoding="utf-8")
    assert "--base main" not in content, (
        "recreate-prs.yml não deve criar PRs com base main."
    )
    parsed = yaml.safe_load(content)
    # Deve estar desativado (sem triggers ativos ou jobs desabilitados)
    on_triggers = parsed.get("on", {})
    assert not on_triggers or on_triggers == {}, (
        "recreate-prs.yml deve ter gatilhos desativados."
    )


def test_sync_public_excludes_internal_and_agent_files():
    """Garante que o workflow sync-public.yml exclua arquivos confidenciais, de agentes e scripts internos."""
    sync_file = WORKFLOWS_DIR / "sync-public.yml"
    assert sync_file.exists(), "Workflow sync-public.yml deve existir"
    content = sync_file.read_text(encoding="utf-8")

    expected_exclusions = [
        "docs/internal",
        ".jules",
        ".kiro",
        ".agents",
        "AGENTS.md",
        "scripts",
        "docs/kiro-credential-sanitization-report.md",
        ".github/dependabot.yml",
        ".github/workflows/sync-public.yml",
    ]
    for exclusion in expected_exclusions:
        assert exclusion in content, (
            f"O workflow sync-public.yml deve conter exclusão explícita para '{exclusion}'."
        )


def test_pr_agent_workflow_is_disabled_or_removed():
    """Garante que pr-agent.yml não execute em eventos automáticos (Issue #229)."""
    pr_agent = WORKFLOWS_DIR / "pr-agent.yml"
    if not pr_agent.exists():
        return
    content = pr_agent.read_text(encoding="utf-8")
    parsed = yaml.safe_load(content)
    on_triggers = parsed.get("on") if "on" in parsed else parsed.get(True, {})
    assert not on_triggers or on_triggers == {}, (
        "pr-agent.yml deve ter gatilhos desativados para evitar ruído de bot."
    )


def test_trigger_bot_pr_does_not_fire_on_push():
    """Garante que trigger-bot-pr.yml não abra PRs a cada push em develop (Issue #229)."""
    trigger_file = WORKFLOWS_DIR / "trigger-bot-pr.yml"
    if not trigger_file.exists():
        return
    content = trigger_file.read_text(encoding="utf-8")
    parsed = yaml.safe_load(content)
    on_triggers = parsed.get("on") if "on" in parsed else parsed.get(True, {})
    assert "push" not in on_triggers, (
        "trigger-bot-pr.yml não deve disparar no evento 'push' para evitar churn de PRs."
    )


def test_single_agents_instruction_file_in_root():
    """Garante que apenas AGENTS.md na raiz exista como instrução de agentes (Issue #229)."""
    repo_root = WORKFLOWS_DIR.parent.parent
    root_agents = repo_root / "AGENTS.md"
    dot_agents = repo_root / ".agents" / "AGENTS.md"
    jules_sentinel = repo_root / ".jules" / "sentinel.md"

    assert root_agents.exists(), "AGENTS.md deve existir na raiz do repositório."
    assert not dot_agents.exists(), ".agents/AGENTS.md duplicado deve ser removido."
    assert not jules_sentinel.exists(), ".jules/sentinel.md deve ser consolidado no AGENTS.md raiz."

    content = root_agents.read_text(encoding="utf-8")
    assert "Sentinel Security Invariants" in content or "Sentinel" in content
    assert "TOCTOU" in content


def test_all_internal_docs_have_historical_record_banner():
    """Garante que todos os documentos em docs/internal/ contenham o banner de registro histórico (Issue #229)."""
    internal_dir = WORKFLOWS_DIR.parent.parent / "docs" / "internal"
    if not internal_dir.exists():
        return

    banner_marker = "REGISTRO HISTÓRICO — NÃO É BACKLOG"
    for md_file in internal_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        assert banner_marker in content, (
            f"O documento {md_file.name} em docs/internal/ deve conter o banner de registro histórico."
        )
