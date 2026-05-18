# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [1.1.1] - 2026-05-16
### Fixed
- Hardcoded credential removed from \utomation/python/fix_ksc_auth.py\
- \.secrets.baseline\ cleaned of references to deleted files
- \scratch/check_api.py\ removed from repository

### Changed
- 65 didactic scripts archived to \utomation/archive/didactic-2026-05/\
