# 1. Visão geral técnica

## 1.1 Ficha do projeto

| Item | Informação |
|---|---|
| Nome | KSC Deployment Runbook |
| Objetivo | Implantação repetível, segura e auditável do KSC 16.x Administration Server e Web Console em Linux |
| Status | Beta — deploy real validado em uma combinação; sem release tagueada `[FATO]` |
| Licença | Apache License 2.0 |
| Repositório | `https://github.com/portosoft/ksc-deployment-runbook` |
| Branch de integração | `develop`; releases via merge para `main` |
| Linguagens | Python 3 (58 arquivos), Bash, YAML (Ansible + GitHub Actions), Markdown |
| Dependências diretas | `pydantic`, `paramiko`, `pyyaml`, `requests`, `cryptography`, `python-dotenv`, `jinja2`, `lxml`, `md2pdf`, `Pillow`; testes: `pytest`, `pytest-cov`, `hypothesis` |
| Ferramenta principal | Kaspersky Security Center 16.x — distribuição Linux (Administration Server, Network Agent, Web Console, serviço IAM) |
| SGBD alvo | PostgreSQL 16.x |
| SO alvo | Rocky Linux 9.x, Oracle Linux 9.x |
| Público-alvo | Administradores de segurança, times de infraestrutura e integradores que operam KSC em Linux |
| Ambiente de execução | Estação ou host de administração executando `kscctl`; alvo remoto via SSH (`paramiko`) ou execução local no servidor |
| Distribuição | Clone do repositório Git; não há pacote publicado em PyPI ou RPM `[FATO]` |
| Requisitos mínimos do alvo | 8 GB RAM (16 GB recomendado), 100 GB+ em `/opt/kaspersky` e `/var/opt/kaspersky` |

## 1.2 Escopo

**Dentro do escopo:** preparação do SO, instalação e tuning do PostgreSQL 16,
verificação de integridade e instalação dos pacotes do KSC, configuração do Web
Console, hardening pós-instalação, auditoria com geração de relatório, rollback
documentado.

**Fora do escopo:** licenciamento Kaspersky, migração de KSC Windows para
Linux, políticas de endpoint pós-deploy, firewalls de borda, versões de KSC
anteriores à 15.0, SGBDs MySQL/MariaDB.

## 1.3 Problema e proposta de valor

### O problema

A instalação do KSC em Linux depende de um conjunto amplo de pré-condições que
falham de forma tardia e com diagnóstico pouco evidente: ausência de
dependências do SO, `LD_LIBRARY_PATH` incompleto para as bibliotecas em
`/opt/kaspersky/ksc64/lib`, contextos SELinux, resolução DNS do FQDN do
servidor, parâmetros de `max_connections` e memória do PostgreSQL,
disponibilidade das portas 443, 8080, 13000, 13291 e 14000, e a configuração do
Web Console e do serviço IAM. `[FATO]` — documentado em
`docs/10-troubleshooting.md` e `docs/03-pre-requisitos.md`.

### Quem é afetado

Equipes que implantam KSC em mais de um servidor, ou que precisam demonstrar,
em auditoria interna ou externa, como um servidor de segurança foi configurado.

### Como é tratado hoje

Pela documentação oficial do produto, seguida manualmente, complementada por
scripts próprios de cada equipe. Essa abordagem é correta e suficiente para uma
instalação única, mas não produz por si só: (a) verificação prévia
automatizada, (b) registro estruturado do que foi executado, (c) garantia de
que dois servidores foram configurados de forma idêntica.

### O que o projeto acrescenta

| Capacidade | Estado |
|---|---|
| Pré-checagem automatizada de SO, DNS, portas, recursos e PostgreSQL antes de instalar | Implementado e coberto por testes unitários `[FATO]` · não validado em alvo real `[NÃO VALIDADO]` |
| Verificação obrigatória de SHA-256 dos RPMs oficiais antes da instalação ("Zero Trust Gate") | Implementado, com catálogo em `configs/ksc/packages.json` e `checksums.sha256`, coberto por `tests/test_packages.py` `[FATO]` |
| Log estruturado em JSON por comando executado, gravado em `evidence/` | Implementado `[FATO]` |
| Relatório de auditoria em Markdown/PDF (`kscctl audit --report`) | Implementado `[FATO]` · conteúdo não conferido contra servidor real `[NÃO VALIDADO]` |
| Contrato CLI uniforme `--check` / `--apply` / `--report` em todos os subcomandos | Implementado e verificado por `tests/test_cli_contracts.py` `[FATO]` |
| Instalação e hardening efetivos | Implementado e **executado com sucesso contra um KSC 16.3.0.1207 real** `[OBSERVADO]` |

### Valor potencial para a Kaspersky

`[HIPÓTESE]` — depende de validação e de interesse da equipe:

- Redução do volume de chamados de suporte relacionados a pré-requisitos, por
  detectá-los antes da instalação.
- Um conjunto concreto e reproduzível de casos de falha em Linux, útil como
  insumo para documentação e para o roadmap do instalador.
- Base para material de referência comunitário em português sobre KSC em Linux.

Nenhum desses benefícios foi medido. Não fazemos afirmação de que o projeto é
"mais rápido", "mais seguro" ou "melhor" que o procedimento manual: não há
comparação controlada, métrica ou ambiente de teste que sustente tal afirmação.

## 1.4 Maturidade

Classificação: **Beta**.

| Área | Estado atual | Evidência | Limitação | Próximo passo |
|---|---|---|---|---|
| Funcionalidade | Ciclo completo executado contra KSC real: instalação, Web Console, pós-check e relatório | `evidence/e2e-209/` | Uma única combinação exercitada | [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227) |
| Integração | Interfaces mapeadas; parte não documentada oficialmente | [03](03-integration-with-main-tool.md) | Dependência de comportamento observado | [#207](https://github.com/portosoft/ksc-deployment-runbook/issues/207), Q1–Q3 |
| Qualidade | 144 testes passam; 2 erros de coleta em arquivos fora de `tests/` | `pytest -q`, 2026-09-13 | Cobertura não publicada; `automation/ops/test_sudo.py` e `automation/smoke-tests/test_api_login.py` quebram a coleta | [#102](https://github.com/portosoft/ksc-deployment-runbook/issues/102) |
| Segurança | Vault com chave 0600, geração sintética de credenciais, CodeQL/Semgrep/baseline de segredos ativos | `.github/workflows/`, `automation/lib/vault.py` | `.env` em texto claro permanece suportado | [#101](https://github.com/portosoft/ksc-deployment-runbook/issues/101) |
| Documentação | Trilha de 14 etapas completa em pt-BR | `docs/` | Sem versão em inglês | [#103](https://github.com/portosoft/ksc-deployment-runbook/issues/103) |
| Operação | Rollback e troubleshooting documentados; laboratório reproduzível com snapshots | `docs/14`, `infra/proxmox/provision-vm.sh` | Rollback ainda não exercitado | [#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223) |
| Compatibilidade | **KSC 16.3.0.1207 + Rocky 9.8 + PG 16 testado**; demais declaradas | `evidence/e2e-209/` | Oracle Linux 9 e outras versões não exercitadas | [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227) |

Os números `#nnn` remetem às issues do GitHub; ver [09-roadmap.md](09-roadmap.md).

## 1.5 Declaração explícita sobre o que é e o que não é comprovado

**Comprovado por execução real** (2026-09-12, `evidence/e2e-209/`):

1. `setup --apply` instala de fato: PostgreSQL 16 provisionado, RPMs oficiais
   verificados e instalados, `postinstall.pl` concluído, hardening aplicado e
   12 serviços ativos, com SELinux em `enforcing` ao final. `[OBSERVADO]`
2. O Web Console responde em HTTPS com HTTP 200. `[OBSERVADO]`
3. O relatório de auditoria é gerado em Markdown e PDF sem falhas críticas.
   `[OBSERVADO]`

**Não comprovado:**

4. Oracle Linux 9 e versões do KSC diferentes da 16.3.0.1207 — [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227).
   `[NÃO VALIDADO]`
5. Rollback sobre instalação parcial — [#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223). `[NÃO VALIDADO]`
6. Idempotência medida por um segundo ciclo comparado — [#228](https://github.com/portosoft/ksc-deployment-runbook/issues/228).
   `[NÃO VALIDADO]`
7. Qualquer característica de desempenho — [#225](https://github.com/portosoft/ksc-deployment-runbook/issues/225). `[NÃO VALIDADO]`

A validação foi feita em **uma execução, em laboratório virtualizado**. Isso
comprova que o caminho funciona; não substitui uso em produção nem operação
continuada.
