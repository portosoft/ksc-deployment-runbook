# Review e Remediação — v2.0

## Contexto

Este documento registra as correções e melhorias aplicadas com base no review comparativo do PR #72,
que analisou o estado do repositório entre o diagnóstico inicial e o snapshot de código da PR.

## Resumo das Ações Realizadas

### Stage 1 — CI Blocker Resolution

| Arquivo | O que foi feito | Motivo |
|---|---|---|
| `tests/test_remote.py` | Migrado de `dummy_config` local (com `# pragma: allowlist secret`) para fixture `ksc_test_config` do `conftest.py` | P0: credenciais hardcoded com pragmas ativos ignoraram o Requirement 4 da spec de sanitização |
| `.github/workflows/ci-integration.yml` | Substituído hardcoded de credenciais por script Python com `generate_password()`; mudado `kscserver.exemplo.ts.net` para `ksc-placeholder.test`; removidos `db reset --check`, `iam purge-mfa --check`, `web fix-config --check` (todos exigiam SSH real) | CI quebrado por SSH inexistente no container Rocky Linux |
| `.github/workflows/codeql.yml` | Hash do `actions/checkout` atualizado de `34e1148...` → `b4ffde65...` | Eliminar warning de Node.js 20 |
| `.github/workflows/recreate-prs.yml` | Mesma atualização de hash | Mesmo motivo |
| `automation/bash/collect-ksc-audit.sh` | Adicionado `# shellcheck shell=bash` após shebang | Prevenir SC2039 falso-positivo em process substitution |
| `automation/bash/validate-ksc.sh` | Adicionado `# shellcheck shell=bash` após shebang | Mesmo motivo |

### Stage 2 — Security Gaps

| Arquivo | O que foi feito | Motivo |
|---|---|---|
| `automation/lib/vault.py` | Adicionada função `_assert_secure()` que verifica permissões 0o600 antes de ler a chave; `ensure_key()` chama a verificação | Se `configs/vault.key` tiver permissões 0o644, a chave seria lida sem aviso |
| `docs/03-pre-requisitos.md` | Nota explícita adicionada: `--vault` grava tanto `secrets.bin` (cifrado) quanto `.env` (plaintext); ambos exigem `chmod 600` | Operador poderia concluir erroneamente que plaintext não persiste |
| `.secrets.baseline` | Ambas as entradas marcadas como `is_verified: true` | Falsos positivos documentados; elimina warning residual no CI |
| `CHECKLIST.md` | Comando corrigido de `init_config.py` para `python3 -m automation.python.init_config` | Conforme apontado pelo CodeRabbit |

### Stage 3 — Architecture Gaps

| Arquivo | O que foi feito | Motivo |
|---|---|---|
| `automation/python/kscctl.py` | Eliminado `sys.argv = [sys.argv[0]]` anti-pattern; agora chama `run_audit_check(config)`, `run_setup_check(config)` etc. diretamente | Quebrava em qualquer contexto onde `sys.argv[0]` não existe |
| `automation/python/ksc_audit.py` | Extraídas funções `run_audit_check()`, `run_audit_postcheck()`, `run_audit_report()` que aceitam `config` como parâmetro | Permite chamada direta sem manipular `sys.argv` |
| `automation/python/ksc_setup.py` | Extraídas funções `run_setup_check()`, `run_setup_apply()` que aceitam `config` como parâmetro | Mesmo motivo |
| `automation/ops/reconfigure_ksc_service.py` | Substituído `client.exec_command(f"sudo -S {run_cmd}")` por `run_remote_sudo(client, ...)` | Duplicava lógica de stdin/EOF já centralizada em `remote.py` |
| `benchmark.py` | Movido para `automation/python/tests/benchmarks/benchmark.py` | Não pertence à raiz do repositório |

## Estado Final dos Testes

```
61 passed, 4 skipped in 6.47s
```

Os 4 skips são `test_secure_file.py` (requer POSIX — Windows não suporta).

## Pendências para PRs Futuros

- Cobertura de docstrings: 43,33% (threshold 80%). Priorizar `shell_utils.py`, `ksc_audit.py`, `ksc_setup.py`, `automation/ops/`
- Tags de release: criar `git tag v1.0.0`, `v1.1.0`, `v1.1.1` alinhadas com CHANGELOG
- `trigger-bot-pr.yml`: atualizar para gerar título e body do PR a partir do último commit ou CHANGELOG `[Unreleased]`
- `ksc_harden_db.py --check`: ainda conecta SSH para ler `postgresql.conf` real (--check deveria ser puramente local)

## Assinatura

Gerado em: 2026-06-16
Por: Revisão Técnica PR #72
