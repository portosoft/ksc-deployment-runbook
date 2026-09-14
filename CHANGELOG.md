# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
- `.github/workflows/ci.yml`: o passo de auto-commit deixa de tentar um push sem
  assinatura GPG, que a proteção do branch recusa — o job falhava em todo push
  para `develop` sem relação com lint ou testes. Sem GPG disponível, a
  divergência passa a ser reportada com o diff e o commit é ignorado.
- `.secrets.baseline` normalizado com a mesma ordenação de chaves que o CI
  aplica (`sort_keys=True`). O arquivo divergia em 120 linhas a cada execução
  apenas por ordem de chaves, o que fazia o auto-commit sempre ter o que
  commitar.

## [2.0.0] — 2026-09-13

Primeira versão com deploy real validado. Até aqui o `setup --apply` era
simulado; a partir desta versão ele instala o produto.

### ⚠️ Mudança de comportamento

- **`kscctl setup --apply` deixou de ser simulação e passou a instalar de
  fato.** Quem tinha o hábito de executá-lo esperando um no-op agora provisiona
  PostgreSQL 16, instala os RPMs do KSC, executa o `postinstall.pl`, configura o
  Web Console e aplica hardening no servidor. Para simular a sequência completa
  sem alterar nada, use `setup --check`.
- **Python 3.10 ou superior passa a ser obrigatório.** O `python3` do Rocky
  Linux 9 é a versão 3.9 e não satisfaz o `requirements.txt`; use o
  `python3.11` do AppStream. Ver issue #231.

### Added

- **Instalação real** (#208): preparação do SO, PostgreSQL 16 com `initdb`
  idempotente e criação condicional de role e bases, instalação dos RPMs com
  gate SHA-256 obrigatório, `postinstall.pl` silencioso com arquivo de respostas
  em modo 0600 removido ao final, e hardening com drop-in de `LD_LIBRARY_PATH`.
- **Configuração do KSC Web Console** (#209): o RPM instala os arquivos, mas quem
  configura o produto é o `setup.js`, com parâmetros em
  `/etc/ksc-web-console-setup.json`. Inclui drop-in de `CAP_NET_BIND_SERVICE`
  quando a porta é privilegiada, sem o qual o serviço reinicia indefinidamente
  sem escutar.
- **`kscctl rollback`** (#223): remoção completa da instalação, com `--verify`
  que percorre o host e falha se sobrar resíduo. Exige `--confirm-token`.
- **`dry_run` em todos os passos de instalação**: `setup --check` passa a simular
  a sequência completa registrando cada comando que seria executado.
- **Laboratório de validação** (#209): `infra/proxmox/provision-vm.sh` provisiona
  a VM de testes com imagem genericcloud e cloud-init, em versão fixada.
- **`automation/bash/state-fingerprint.sh`** (#228): impressão determinística do
  estado do host, para verificar idempotência por diff.
- **Evidências das validações** em `evidence/e2e-209/`, `e2e-223/` e `e2e-228/`.
- `tests/test_requirements.py` (#101): impede que dependências mortas voltem.

### Fixed

Defeitos revelados pela primeira execução contra um KSC real — nenhum deles era
detectável por teste unitário:

- `libidn` não existe no EL9; o pacote é `libidn2` (#209).
- O grupo `kladmins` e a conta de serviço precisam existir **antes** do
  instalador, que os valida mas não os cria (#209).
- **O hardening derrubava o produto**: `chmod -R o-rwx` retirava do `klserver` o
  acesso aos próprios binários (203/EXEC) e do Web Console o acesso ao diretório
  de trabalho (200/CHDIR) (#209).
- `ksc-web-console.service` não existe; as unidades reais são `KSCWebConsole`,
  `KSCSvcWebConsole`, `KSCWebConsoleManagement`, `KSCWebConsoleNATS` e
  `KSCWebConsolePlugin` (#209).
- `setup --apply` não era idempotente: o `postinstall.pl` recusa reexecução e as
  portas ocupadas pelo próprio KSC reprovavam o pré-check (#209, #228).
- A reexecução **substituía o certificado TLS** do Web Console e recriava suas
  contas de serviço, sem que o relatório de auditoria acusasse mudança (#228).
- A busca da unidade do PostgreSQL parava em `postgresql` e nunca chegava a
  `postgresql-16`, reprovando o pós-check com o banco ativo (#209).
- O **PDF de auditoria nunca era gerado**: a chamada usava a assinatura da linha
  1.x do `md2pdf` e as bibliotecas do WeasyPrint não eram instaladas (#209).
- O relatório reexecutava o pré-check em servidor instalado, acusando como
  crítico as portas que o KSC passou a ocupar (#209).
- Falhas silenciosas no rollback e no setup, apontadas em revisão de código:
  passos destrutivos que reportavam sucesso após falhar, verificação que
  anunciava host limpo sem ter conseguido inspecionar, e consulta ao PostgreSQL
  sem o endpoint configurado.
- `black` e `isort` desfaziam o trabalho um do outro a cada execução do
  pre-commit (#234).

### Changed

- `docs/11-rollback.md` reescrito: o procedimento anterior deixava sete resíduos,
  entre eles o RPM `klnagent64`, a base `ksciam` e uma role `ksc_admin` que o
  runbook nunca cria (#223).
- `docs/14-ambiente-testes-proxmox.md`: provisionamento automatizado no lugar dos
  passos manuais de interface web.
- `requirements.txt` (#101): removidas `python-dotenv`, `jinja2`, `lxml` e
  `Pillow` — a primeira sem uso algum, as demais transitivas do `md2pdf`.
- `.secrets.baseline` (#101): de 22 achados, todos falsos positivos, para zero.
- `run_command` aceita `input_data`, mantendo senhas e SQL fora da lista de
  processos do servidor.
- `infra/proxmox/compose.yml`: nome de projeto fixo `ksc-lab`, para não colidir
  com outros laboratórios homônimos no mesmo host.

### Security

- Verificação SHA-256 obrigatória dos pacotes antes de qualquer instalação.
- SELinux restaurado para `enforcing` ao final, inclusive em caso de erro.
- Drop-in de `CAP_NET_BIND_SERVICE` removido quando a porta deixa de ser
  privilegiada (CWE-250).

### Conhecido e não resolvido

- Validação em **uma única combinação**: Rocky Linux 9.8 + KSC 16.3.0.1207 +
  PostgreSQL 16. Oracle Linux 9 e outras versões seguem declaradas (#227).
- Nenhuma métrica de desempenho coletada (#225).
- `.env` em texto claro ainda é caminho suportado (#237).


## [1.1.1] - 2026-05-16
### Fixed
- Hardcoded credential removed from \utomation/python/fix_ksc_auth.py\
- \.secrets.baseline\ cleaned of references to deleted files
- \scratch/check_api.py\ removed from repository

### Changed
- 65 didactic scripts archived to \utomation/archive/didactic-2026-05/\

## [1.1.0] - 2026-05-16
### Added
- Arquitetura DevSecOps em Python (`automation/python/`).
- Módulos utilitários para logs, prechecks e deploy (`config.py`, `shell_utils.py`, `logging_utils.py`, `checks.py`, `setup_steps.py`).
- Sistema de evidências via JSON Lines e geração de relatórios com `report_utils.py`.
- Suite de testes via `pytest` validando os contratos CLI (`tests/test_cli_contracts.py`).
- Workflow de CI/CD para GitHub Actions (`.github/workflows/ci.yml`).
- Documentos de governança `CONTRATOS_AUTOMACAO.md` e `EVIDENCIAS.md`.
- Placeholders para os 12 passos da jornada em `docs/`.

### Changed
- `ksc_audit.py` e `ksc_setup.py` refatorados para consumir a nova arquitetura de forma modular.
- Expansão do `.pre-commit-config.yaml` com hooks para `black`, `flake8`, `yamllint`, `shellcheck`.
- Atualização do `README.md` (A Jornada do Operador) e `CONTRIBUTING.md` (DevSecOps).

## [1.0.0] - 2026-05-13
### Added
- Nova estrutura de documentação numerada (00-12).
- Diagnóstico executivo inicial.
- Checklist de aceite operacional.
- Contrato operacional entre scripts e variáveis.
- Templates de Issue e PR.

### Changed
- README.md reescrito com foco em SRE e operações.
- Consolidação de scripts de automação.

### Fixed
- Removidas redundâncias de documentação.
- Padronização de termos técnicos.
