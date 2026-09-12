# 1. Visão geral técnica

## 1.1 Ficha do projeto

| Item | Informação |
|---|---|
| Nome | KSC Deployment Runbook |
| Objetivo | Implantação repetível, segura e auditável do KSC 16.x Administration Server e Web Console em Linux |
| Status | MVP / Beta inicial — sem release tagueada `[FATO]` (`git tag` vazio) |
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
| Instalação e hardening efetivos | Implementado de fato em `setup_steps.py` e coberto por 16 testes unitários `[FATO]` · nunca executado em servidor real `[NÃO VALIDADO]` |

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

Classificação: **MVP / Beta inicial**.

| Área | Estado atual | Evidência | Limitação | Próximo passo |
|---|---|---|---|---|
| Funcionalidade | Auditoria, pré-check, verificação de pacotes e instalação implementados | `automation/python/setup_steps.py`, `tests/test_setup_steps.py` | Nunca executada em servidor real | [#209](https://github.com/portosoft/ksc-deployment-runbook/issues/209) (E2E) |
| Integração | Interfaces mapeadas; parte não documentada oficialmente | [03](03-integration-with-main-tool.md) | Dependência de comportamento observado | [#207](https://github.com/portosoft/ksc-deployment-runbook/issues/207), Q1–Q3 |
| Qualidade | 124 testes passam; 2 erros de coleta em arquivos fora de `tests/` | `pytest -q`, 2026-09-12 | Cobertura não publicada; `automation/ops/test_sudo.py` e `automation/smoke-tests/test_api_login.py` quebram a coleta | [#102](https://github.com/portosoft/ksc-deployment-runbook/issues/102) |
| Segurança | Vault com chave 0600, geração sintética de credenciais, CodeQL/Semgrep/baseline de segredos ativos | `.github/workflows/`, `automation/lib/vault.py` | `.env` em texto claro permanece suportado | [#101](https://github.com/portosoft/ksc-deployment-runbook/issues/101) |
| Documentação | Trilha de 14 etapas completa em pt-BR | `docs/` | Sem versão em inglês | [#103](https://github.com/portosoft/ksc-deployment-runbook/issues/103) |
| Operação | Rollback e troubleshooting documentados | `docs/11-rollback.md`, `docs/10-troubleshooting.md` | Rollback não exercitado em ambiente real | [#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223) |
| Compatibilidade | Declarada para KSC 16.x / PG 16 / RL9 · OL9 | `README.md`, `docs/02-matriz-compatibilidade.md` | Nenhuma combinação testada em servidor real | [#209](https://github.com/portosoft/ksc-deployment-runbook/issues/209) |

Os números `#nnn` remetem às issues do GitHub; ver [09-roadmap.md](09-roadmap.md).

## 1.5 Declaração explícita sobre o que ainda não é real

Para evitar leitura otimista deste pacote, registramos de forma destacada:

1. `setup_steps.py` executa comandos reais desde [#209](https://github.com/portosoft/ksc-deployment-runbook/issues/209) (dnf, initdb, psql,
   instalação dos RPMs, `postinstall.pl`, drop-in systemd, systemctl), com
   suporte a `dry_run` e cobertura unitária. Nenhum desses comandos foi
   executado contra um servidor KSC real. `[NÃO VALIDADO]`
2. Os 16 arquivos em `evidence/` foram produzidos por execução de testes com
   transporte SSH simulado — contêm `"stdout": "stdout"` e hosts fictícios.
   **Não são evidência de deploy em servidor real.** `[FATO]`
3. Nenhuma instalação do KSC 16.x foi executada de ponta a ponta por este
   projeto em um servidor Rocky/Oracle Linux 9 com registro público.
   `[NÃO VALIDADO]`
