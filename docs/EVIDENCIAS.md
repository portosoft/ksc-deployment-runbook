# Gestão de Evidências

A observabilidade do deployment do KSC é governada através do registro de logs estruturados armazenados no diretório `evidence/`. O objetivo principal é garantir que nenhuma etapa seja feita "às cegas" e que exista sempre um registro de auditoria do estado do servidor.

## Estrutura de Diretórios

As evidências são organizadas cronologicamente pelo tipo de execução, sob o formato `YYYYMMDD-HHMMSS`:

```
evidence/
├── precheck/
│   └── YYYYMMDD-HHMMSS/
│       └── run.log
├── deploy/
│   └── YYYYMMDD-HHMMSS/
│       └── run.log
├── postcheck/
│   └── YYYYMMDD-HHMMSS/
│       └── run.log
└── reports/
    └── YYYYMMDD-HHMMSS/
        ├── report.md
        └── report.pdf
```

## Logs em Formato JSON Lines

O arquivo `run.log` utiliza o formato `JSON Lines` para armazenar eventos padronizados da instalação. Cada linha é um evento estruturado, o que facilita o parse por ferramentas como Splunk, ELK, ou pequenos scripts jq.

Exemplo de Log:
```json
{"event": "precheck_start", "timestamp": "2026-05-16T12:00:00Z"}
{"event": "precheck_result", "timestamp": "2026-05-16T12:00:05Z", "has_critical": false, "total_items": 4}
```

## Relatórios

A execução do comando `ksc_audit.py --report` vai aglutinar e extrair do último estado de verificação um relatório consolidado com formatação em Markdown e PDF, salvando-o no diretório `reports/`.
