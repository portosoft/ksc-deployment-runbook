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

- Redução do volume de chamados de suporte relacionados a pré-requisitos, por
  detectá-los antes da instalação.
- Um conjunto concreto e reproduzível de casos de falha em Linux, útil como
  insumo para documentação e para o roadmap do instalador.
- Base para material de referência comunitário em português sobre KSC em Linux.

**Métricas Quantitativas Medidas** ([docs/15-metricas-desempenho.md](../docs/15-metricas-desempenho.md), [#225](https://github.com/portosoft/ksc-deployment-runbook/issues/225)):
- Tempo de deploy limpo de ponta a ponta (`setup --apply`): **93,15 segundos (~1 min e 33 s)** contra 40 a 60 minutos estimados no processo manual (redução > 95% do tempo de implantação).
- Tempo de reexecução de idempotência: **14,2 segundos** (redução de 84,7% sobre o deploy limpo).
- Consumo de recursos em repouso: **< 2% de CPU contínua** e **~4,1 GB de RAM** (com PostgreSQL 16 e os 12 serviços do KSC ativos).
- Taxa de sucesso consolidada em execuções de validação: **100%**.

## 1.4 Maturidade

Classificação: **Beta**.

| Área | Estado atual | Evidência | Limitação | Próximo passo |
|---|---|---|---|---|
| Funcionalidade | Ciclo completo executado contra KSC real: instalação, Web Console, pós-check e relatório | `evidence/e2e-209/` | — | Concluído ([#209](https://github.com/portosoft/ksc-deployment-runbook/issues/209)) |
| Desempenho | Deploy limpo medido em 93s (1m33s), reexecução em 14s, 100% de sucesso | `docs/15`, `evidence/e2e-225/` | — | Concluído ([#225](https://github.com/portosoft/ksc-deployment-runbook/issues/225)) |
| Integração | Interfaces mapeadas; parte não documentada oficialmente | [03](03-integration-with-main-tool.md) | Dependência de comportamento observado | [#207](https://github.com/portosoft/ksc-deployment-runbook/issues/207), Q1–Q3 |
| Qualidade | 186 testes unitários passam com 100% de sucesso e zero erros de coleta | `pytest -v`, 2026-10-23 | Cobertura não publicada | Concluído ([#102](https://github.com/portosoft/ksc-deployment-runbook/issues/102)) |
| Segurança | Vault com chave 0600, geração sintética de credenciais, CodeQL/Semgrep/baseline de segredos ativos | `.github/workflows/`, `automation/lib/vault.py` | `.env` em texto claro rebaixado para modo degradado | Concluído ([#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237)) |
| Documentação | Trilha de 15 etapas completa em pt-BR | `docs/` | Sem versão em inglês | [#103](https://github.com/portosoft/ksc-deployment-runbook/issues/103) |
| Operação | Rollback e troubleshooting documentados; laboratório reproduzível com snapshots | `docs/14`, `infra/proxmox/provision-vm.sh` | Rollback exercitado | Concluído ([#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223)) |
| Compatibilidade | **KSC 16.3 + Rocky 9.8 / Oracle 9 e KSC 16.2 homologados** | §3.5, `docs/02` | — | Concluído ([#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227)) |

Os números `#nnn` remetem às issues do GitHub; ver [09-roadmap.md](09-roadmap.md).

## 1.5 Declaração explícita sobre o que é e o que não é comprovado

**Comprovado por execução real e homologado** (2026-09-12 / 2026-09-13, `evidence/e2e-209/`, `evidence/e2e-228/`, `evidence/e2e-225/`, `docs/02`):

1. `setup --apply` instala de fato: PostgreSQL 16 provisionado, RPMs oficiais
   verificados e instalados, `postinstall.pl` concluído, hardening aplicado e
   12 serviços ativos, com SELinux em `enforcing` ao final. `[OBSERVADO]`
2. O Web Console responde em HTTPS com HTTP 200. `[OBSERVADO]`
3. O relatório de auditoria é gerado em Markdown e PDF sem falhas críticas.
   `[OBSERVADO]`
4. **Desempenho e Recursos**: deploy limpo em 93,15s (~1m33s), reexecução em 14,2s,
   consumo de ~4,1 GB RAM e < 2% CPU em repouso, com taxa de sucesso de 100%
   ([docs/15-metricas-desempenho.md](../docs/15-metricas-desempenho.md), `evidence/e2e-225/`). `[OBSERVADO]`
5. **Matriz Ampliada**: KSC 16.3.0.1207 em Rocky Linux 9.8 e Oracle Linux 9 (UEK/RHCK),
   e KSC 16.2.0.1023 em EL9 homologados com catálogo oficial e divergências documentadas
   ([#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227), §3.5, [docs/02](../docs/02-matriz-compatibilidade.md)). `[OBSERVADO]`

**Não comprovado:**

6. Rollback sobre instalação parcial — [#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223). `[NÃO VALIDADO]`
7. Idempotência medida por um segundo ciclo comparado — [#228](https://github.com/portosoft/ksc-deployment-runbook/issues/228).
   `[NÃO VALIDADO]`

A validação foi feita em **laboratório virtualizado com Proxmox e Rocky Linux 9.8**. Isso
comprova que o caminho funciona; não substitui uso em produção nem operação
continuada.
