# 5. Testes, validação e evidências

## 5.1 Resultado da suíte de testes

| Item | Resultado |
|---|---|
| Comando | `python3 -m pytest -q` |
| Data | 2026-09-12 |
| Ambiente | Linux, Python 3, branch `develop`, commit `704a9bd` |
| Resultado | **144 testes aprovados**, 66 warnings, **2 erros de coleta** |
| Erros de coleta | `automation/ops/test_sudo.py::test_sudo` e `automation/smoke-tests/test_api_login.py::test_login` — arquivos fora de `tests/` que exigem ambiente real e são coletados indevidamente pelo pytest |
| Cobertura | `pytest-cov` disponível; **percentual não publicado** `[LIMITAÇÃO]` |

`[OBSERVADO]` — reproduzível no repositório.

## 5.2 O que os testes cobrem

| Área | Arquivo | Natureza |
|---|---|---|
| Pré-checagens | `tests/test_checks.py` | Unitário com mocks |
| Contrato da CLI (`--check`/`--apply`/`--report`) | `tests/test_cli_contracts.py` | Unitário |
| Configuração e validação `pydantic` | `tests/test_config.py`, `tests/test_init_config.py` | Unitário |
| Geração de credenciais sintéticas | `tests/test_credentials.py`, `tests/test_credentials_properties.py` | Unitário + property-based (`hypothesis`) |
| Catálogo e integridade de pacotes | `tests/test_packages.py` | Unitário |
| Auditoria | `tests/test_ksc_audit.py` | Unitário |
| Execução remota | `tests/test_remote.py` | Unitário com SSH simulado |
| Arquivos seguros e utilitários de shell | `tests/test_secure_file.py`, `tests/test_shell_utils.py` | Unitário |
| Conversão env → Ansible | `tests/test_env_to_ansible.py` | Unitário |
| Relatórios | `tests/test_report_utils.py` | Unitário |
| Passos de instalação (SO, PostgreSQL, RPM, hardening) | `tests/test_setup_steps.py` | Unitário com `run_command` interceptado |
| Operações (`automation/ops`) | `tests/ops/` | Unitário |

## 5.3 O que os testes unitários **não** cobrem

Os itens abaixo permanecem fora do alcance da suíte unitária. Os três
primeiros passaram a ser cobertos pela validação E2E descrita em §5.6; os
demais continuam abertos.

- Instalação real do KSC 16.x — **coberto por §5.6** `[OBSERVADO]`
- Comportamento real do `postinstall.pl` — **coberto por §5.6** `[OBSERVADO]`
- Configuração real do Web Console — **coberto por §5.6** `[OBSERVADO]`
- Aplicação real das regras nftables. `[LIMITAÇÃO]`
- Rollback executado sobre uma instalação parcialmente concluída — issue
  [#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223). `[LIMITAÇÃO]`
- Desempenho, consumo de recursos, volume e concorrência — **nenhuma métrica
  foi coletada**; issue [#225](https://github.com/portosoft/ksc-deployment-runbook/issues/225). `[LIMITAÇÃO]`
- Segunda execução completa comparando relatórios, para medir idempotência —
  issue [#228](https://github.com/portosoft/ksc-deployment-runbook/issues/228). `[LIMITAÇÃO]`

## 5.4 Natureza dos artefatos em `evidence/`

O diretório contém dois conjuntos de origens diferentes, e a distinção importa.

**`evidence/e2e-209/` — execuções reais.** Produzidas em 2026-09-12 contra um
KSC 16.3.0.1207 instalado em Rocky Linux 9.8. Incluem o log completo do
`setup --apply`, o pós-check, o relatório de auditoria em Markdown e PDF e a
verificação externa do Web Console. São a base de tudo o que este pacote
afirma sobre comportamento real. `[OBSERVADO]`

**Os demais `run.log` — execuções simuladas.** Formato JSON linha-a-linha com
eventos como `reconfigure_start` e `reset_db_success`. Demonstram **que o
mecanismo de evidências funciona e qual é o seu formato**, e nada além disso:
os campos de saída contêm literais como `"stdout": "stdout"` e os hosts são
`127.0.0.1` e `test.ksc.local`. `[FATO]`

Ler os arquivos do segundo grupo como comprovação de instalação seria
incorreto, e por isso mantemos o registro explícito.

## 5.5 CI/CD

| Workflow | Função |
|---|---|
| `ci.yml` | Lint e testes |
| `ci-integration.yml` | Execução dos subcomandos em container Rocky Linux, sem SSH real |
| `codeql.yml` | Análise estática de segurança |
| `semgrep.yml`, `aikido.yml` | Regras adicionais de segurança |
| `pr-rules-enforcer.yml`, `pr-agent.yml` | Governança de PRs |
| `sync-develop.yml` | Sincronização `main` → `develop` após release |
| `cleanup-branches.yml`, `recreate-prs.yml`, `trigger-bot-pr.yml` | Automação de manutenção — **fonte de duplicação de trabalho, ver [09-roadmap.md](09-roadmap.md) §0** |

`ci-integration.yml` deliberadamente não executa `db reset --check`,
`iam purge-mfa --check` e `web fix-config --check`, porque exigem SSH real
indisponível no runner. Essa é a razão técnica pela qual a validação E2E
precisa do laboratório Proxmox e não do CI. `[FATO]`

## 5.6 Validação end-to-end executada

`infra/proxmox/` define um Proxmox VE 9.x em container Podman rootless com
acesso a `/dev/kvm` e sidecars `socat` mapeando as portas do host para a VM de
teste. O provisionamento da VM é automatizado por `infra/proxmox/provision-vm.sh`
(imagem genericcloud do Rocky 9 e cloud-init), de modo que o ambiente é
recriável de forma idêntica.

### Ambiente

| Item | Valor |
|---|---|
| Data | 2026-09-12 |
| Hypervisor | Proxmox VE 9.2.11 em Podman rootless 5.7.0 |
| VM | 4 vCPU, 16 GB RAM, 120 GB, NIC e1000 |
| SO | Rocky Linux 9.8, kernel 5.14.0-687.10.1.el9_8.0.1 |
| Produto | KSC 16.3.0.1207, RPMs oficiais verificados por SHA-256 |
| SGBD | PostgreSQL 16 (repositório PGDG) |
| Python | 3.11.13 do AppStream — ver [#231](https://github.com/portosoft/ksc-deployment-runbook/issues/231) |
| SELinux | `Enforcing` antes, durante a verificação e ao final |

### Resultados

| Etapa | Resultado |
|---|---|
| `audit --check` | exit 0 |
| `packages --download` e `--verify-dir` | 3 RPMs oficiais, íntegros |
| `setup --check` (dry-run) | exit 0, sem alterar o sistema |
| **`setup --apply`** | **exit 0 — instalação real, a partir de snapshot limpo** |
| Web Console | `https://127.0.0.1:8443` → HTTP 200 em `/login` |
| `audit --postcheck` | exit 0, zero falhas críticas |
| `audit --report` | Markdown e PDF, zero falhas críticas |
| Estado final | 12 serviços `active` |

Evidências brutas em `evidence/e2e-209/`.

### Dez defeitos revelados pela execução real

Nenhum era detectável por teste unitário. Todos foram corrigidos e cobertos
por testes de regressão antes de qualquer alegação de sucesso.

| Sintoma observado | Natureza do defeito |
|---|---|
| `Unable to find a match: libidn` | Pré-requisito inexistente no EL9 (é `libidn2`) |
| `But the kladmins group does not exist` | Contas de sistema exigidas pelo instalador não eram criadas |
| `klserver`: `Permission denied`, `203/EXEC` | **O hardening do próprio runbook removia do serviço o acesso aos seus binários** |
| Web Console: `200/CHDIR` | O hardening recursivo do diretório de dados derrubava contas criadas pelo instalador |
| `Do not run the postinstall.pl script again` | `setup --apply` não era idempotente |
| Web Console sem unidade e sem porta | A configuração do componente não era executada |
| Web Console reiniciando sem escutar na 443 | A unidade do instalador não tem `CAP_NET_BIND_SERVICE` |
| `[CRITICAL] postgresql: Inativo` com o banco ativo | A busca da unidade não chegava a `postgresql-16` |
| PDF de auditoria nunca gerado | Assinatura do `md2pdf` incorreta, encoberta por dependência de sistema ausente |
| Relatório com críticos falsos de porta | O pré-check era reexecutado em servidor já instalado |

O terceiro caso merece registro em separado: **o hardening proposto pelo
runbook tornava o produto inoperante**. O que o expôs foi a verificação de
serviços ativos ao final do hardening; sem ela, a instalação teria sido
reportada como bem-sucedida com o Administration Server parado. A lição vale
para a revisão: passos de hardening precisam ser acompanhados de verificação
funcional, não apenas de execução sem erro.

## 5.7 Evidências ainda faltantes

Lista consolidada do que precisamos produzir antes de qualquer alegação de
compatibilidade ou de prontidão para piloto:

Itens já obtidos, registrados em `evidence/e2e-209/`:

1. ~~Log completo de `setup --apply` em Rocky Linux 9 com KSC real~~ — obtido,
   com a versão exata do produto registrada.
2. ~~Relatório `audit --report` gerado a partir de um servidor real~~ — obtido
   em Markdown e PDF.
3. ~~Verificação do Web Console acessível via HTTPS após o deploy~~ — obtida.

Itens ainda faltantes:

4. Log equivalente em Oracle Linux 9 — [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227).
5. Execução em ao menos uma versão menor distinta do KSC 16.x — [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227).
6. Execução de rollback sobre uma instalação parcial — [#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223).
7. Um segundo deploy no mesmo ambiente demonstrando idempotência medida —
   [#228](https://github.com/portosoft/ksc-deployment-runbook/issues/228).
8. Tempo total de execução e consumo de recursos — [#225](https://github.com/portosoft/ksc-deployment-runbook/issues/225).
9. Verificação das regras nftables no alvo real — [#205](https://github.com/portosoft/ksc-deployment-runbook/issues/205).
10. Percentual de cobertura de testes publicado no CI — [#102](https://github.com/portosoft/ksc-deployment-runbook/issues/102).
