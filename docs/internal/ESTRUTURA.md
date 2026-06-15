# Nova Estrutura do Repositório (Arquitetura Proposta)

```text
.
├── README.md                   # Porta de entrada operacional (Reescrito)
├── CHANGELOG.md                # Histórico de mudanças técnico
├── CONTRIBUTING.md             # Guia para novos mantenedores
├── SECURITY.md                 # Política de segurança e reporte de vulnerabilidades
├── VERSIONING.md               # Definição de versionamento (SemVer)
├── DIAGNOSTICO.md              # Relatório de auditoria (Concluído)
│
├── .github/
│   ├── workflows/
│   │   ├── ci-docs.yml         # Lint de Markdown e links
│   │   └── ci-scripts.yml      # Lint de Python e Bash
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
│
├── docs/                       # Jornada do Operador (00-12)
│   ├── 00-index.md             # Mapa da documentação
│   ├── 01-visao-geral.md       # Arquitetura e Escopo
│   ├── 02-matriz-compatibilidade.md
│   ├── 03-pre-requisitos.md    # Infra, Hardware e Acessos
│   ├── 04-precheck.md          # Script de validação automática
│   ├── 05-instalacao-postgresql.md
│   ├── 06-instalacao-ksc.md    # Server + Web Console
│   ├── 07-pos-instalacao-validacao.md
│   ├── 08-hardening.md         # Segurança e Performance
│   ├── 09-operacao.md          # Backup, Restore e Manutenção
│   ├── 10-troubleshooting.md   # Base de conhecimento de erros
│   ├── 11-rollback.md          # Procedimento de emergência
│   ├── 12-faq.md
│   └── contrato-operacional.md # Relação entre arquivos e vars
│
├── automation/
│   ├── ansible/                # Playbooks consolidados
│   ├── bash/                   # Scripts auxiliares de SO
│   ├── python/                 # Scripts principais padronizados
│   │   ├── ksc_setup.py
│   │   ├── ksc_audit.py
│   │   └── ksc_harden_db.py
│   ├── archive/                # Scripts antigos/debug (Saneamento)
│   └── smoke-tests/            # Testes de validação pós-deploy
│
├── configs/
│   ├── env/
│   │   └── ksc_vars.env.example
│   ├── postgres/
│   │   └── postgresql.conf.template
│   ├── ksc/
│   │   └── ksc_response.txt.template
│   └── examples/
│
├── diagrams/                   # Mermaid ou PNGs de arquitetura
└── evidence/                   # Pasta para logs e evidências (Ignorada no Git)
    └── samples/                # Exemplos de logs de sucesso
```

### Justificativas:
1. **Numeração em `docs/`**: Elimina a dúvida de "por onde começo". Segue a ordem cronológica da implantação.
2. **Pasta `archive/`**: Remove o ruído da pasta `automation/` principal sem deletar scripts que podem ser úteis em casos raros.
3. **Templates Explicitados**: Arquivos de configuração agora terminam em `.template` para reforçar que precisam ser preenchidos.
4. **Pasta `evidence/`**: Introduz o conceito de "Auditabilidade". O operador deve salvar evidências aqui.
