# 5. Testes, validação e evidências

## 5.1 Resultado da suíte de testes

| Item | Resultado |
|---|---|
| Comando | `python3 -m pytest -q` |
| Data | 2026-09-12 |
| Ambiente | Linux, Python 3, branch `develop`, commit `704a9bd` |
| Resultado | **124 testes aprovados**, 66 warnings, **2 erros de coleta** |
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

## 5.3 O que os testes **não** cobrem

- Instalação real do KSC 16.x. `[LIMITAÇÃO]`
- Comportamento real do `postinstall.pl`. `[LIMITAÇÃO]`
- Configuração real do Web Console e do serviço IAM. `[LIMITAÇÃO]`
- Aplicação real das regras nftables e dos contextos SELinux. `[LIMITAÇÃO]`
- Rollback executado sobre uma instalação parcialmente concluída. `[LIMITAÇÃO]`
- Desempenho, consumo de recursos, volume e concorrência — **nenhuma métrica de
  desempenho foi coletada em momento algum.** `[LIMITAÇÃO]`

## 5.4 Natureza dos artefatos em `evidence/`

Existem 16 arquivos `run.log` em `evidence/`, com formato JSON linha-a-linha e
eventos como `reconfigure_start`, `run_command_start`, `run_command_end`,
`reset_db_success`. Eles demonstram **que o mecanismo de evidências funciona e
qual é o seu formato**.

Eles **não** demonstram um deploy real: os campos de saída contêm literais como
`"stdout": "stdout"` e os hosts são `127.0.0.1` e `test.ksc.local`. São
produtos de execução de testes com transporte simulado. `[FATO]`

Qualquer leitura desses arquivos como comprovação de instalação bem-sucedida
seria incorreta, e por isso o registramos aqui de forma explícita.

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

## 5.6 Laboratório de validação planejado

`infra/proxmox/` define um Proxmox VE 9.x em container Podman rootless com
acesso a `/dev/kvm` e sidecars `socat` mapeando as portas do host para a VM de
teste `172.30.5.10` (2222→22, 8443→443, 8080→8080, 13291, 13000, 14000, 5432).
O ambiente está **definido e documentado**; a execução do ciclo E2E completo
sobre ele ainda não foi realizada nem registrada. `[NÃO VALIDADO]`

## 5.7 Evidências ainda faltantes

Lista consolidada do que precisamos produzir antes de qualquer alegação de
compatibilidade ou de prontidão para piloto:

1. Log completo de `kscctl setup --apply` em Rocky Linux 9 com KSC 16.x real,
   com versão exata do produto registrada.
2. Log equivalente em Oracle Linux 9.
3. Relatório `kscctl audit --report` gerado a partir de um servidor real.
4. Captura do Web Console acessível em HTTPS/443 após o deploy automatizado.
5. Execução de rollback sobre uma instalação parcial, com estado final
   verificado.
6. Verificação das regras nftables e dos contextos SELinux no alvo real.
7. Percentual de cobertura de testes publicado no CI.
8. Um segundo deploy no mesmo ambiente demonstrando idempotência.
9. Tempo total de execução e consumo de recursos, para substituir hipóteses por
   números.
10. Execução em ao menos uma versão menor distinta do KSC 16.x, para exercitar
    a hipótese de estabilidade das interfaces.
