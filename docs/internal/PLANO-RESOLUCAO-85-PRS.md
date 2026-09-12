> **REGISTRO HISTÓRICO — NÃO É BACKLOG.**
> Este documento é preservado como registro. O backlog válido do projeto está no
> [board](https://github.com/orgs/portosoft/projects/1) e nas
> [issues](https://github.com/portosoft/ksc-deployment-runbook/issues) do GitHub.

# Plano de Resolução e Saneamento das 85 Pull Requests Abertas

Este plano estabelece a estratégia completa para resolver, consolidar e higienizar as **85 Pull Requests em aberto** no repositório `portosoft/ksc-deployment-runbook` antes de prosseguir com a execução do planejamento arquitetural.

---

## Censo e Diagnóstico das 85 PRs

Após análise exaustiva da API do GitHub (`gh pr list`), o universo de 85 PRs abertas divide-se precisamente em 4 categorias:

| Categoria | Quantidade | Destino | Descrição / Causa-Raiz |
|---|---|---|---|
| **Sentinel / Jules Bot** | **66 PRs** | `main` | PRs duplicadas geradas ciclicamente pelo Jules/Sentinel tentando corrigir os mesmos 2 problemas de segurança (CWE-377 e injeção de comando sed) diretamente contra `main`. |
| **Dependabot** | **17 PRs** | `develop` | Atualizações de dependências Python (12 PRs, com duplicatas e versões superadas) e GitHub Actions (5 PRs, incluindo uma conflitante e uma com falha). |
| **Release PR (#210)** | **1 PR** | `main` | PR automatizado de release `develop → main` com 9 commits validados e 18/18 checks CI verdes, aguardando aprovação e merge do Code Owner (`@mendsec`). |
| **Feature Proxmox (#211)** | **1 PR** | `develop` | PR da issue #204 (`feat/204-proxmox-test-environment`), base do planejamento da esteira de testes locais. |
| **Total** | **85 PRs** | — | — |

---

## Decisões de Governança

1. **Fechamento em Lote das 66 PRs do Sentinel**:
   Todas as 66 PRs do Sentinel foram abertas incorretamente contra a branch `main` e repetem indefinidamente correções para os mesmos arquivos (`reconfigure_ksc_service.py` e `fix_web_console_config.py`).
   - Aplicar a correção de segurança canônica diretamente na branch `develop`.
   - Fechar todas as 66 PRs duplicadas com justificativa de rastreabilidade.
   - Deletar as 66 branches remotas geradas pelo bot.

2. **Consolidação das Dependências do Dependabot**:
   Das 17 PRs do Dependabot:
   - PR #158 (`cryptography 50.0.0`) está superada pela #191 (`cryptography 50.0.1`).
   - PR #132 (`pillow 12.3.0`) é duplicata da #140.
   - PR #107 (`actions/checkout` v7) é inválida e está em estado conflitante.
   - PR #130 (`codeql-action/autobuild`) está com falha de execução no CI.
   - Consolidar todas as dependências válidas e atualizadas em branch `chore/deps-consolidation` direcionada à `develop`, fechando as PRs obsoletas/conflitantes.

3. **Promoção do Release PR #210**:
   O PR #210 (`chore(release): merge develop → main`) possui 18/18 checks aprovados e cumpre todos os requisitos de governança. Promovê-lo para `main` formaliza a estratégia DevSecOps em produção e aciona a sincronização automática (`sync-develop.yml`).

4. **Preservação do PR #211 (Proxmox Lab)**:
   O PR #211 permanecerá íntegro e atualizado com `develop`, sendo o ponto focal da próxima etapa do planejamento arquitetural.
