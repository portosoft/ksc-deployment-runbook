# Evidências de Métricas de Desempenho e QA — Issue #225

Este diretório consolida a trilha de auditoria quantitativa sobre tempo total de deploy, consumo de recursos de hardware e taxa de sucesso do deploy automatizado do Kaspersky Security Center 16.x.

## Origem dos Dados

Os dados foram coletados diretamente a partir dos logs de eventos com carimbo de data/hora ISO 8601 UTC de alta precisão gravados nas validações ponta a ponta:
- `evidence/e2e-209/04-setup-apply.log`: Deploy limpo inicial a partir do snapshot `clean-baseline` (93,15 segundos).
- `evidence/e2e-228/01-segunda-execucao.log`: Reexecução de validação de idempotência sobre o host ativo (14,2 segundos).
- `evidence/e2e-223/01-rollback-instalacao-parcial.log`: Rollback completo e verificado de instalação parcial.

## Arquivos

| Arquivo | Descrição |
| :--- | :--- |
| `metrics.json` | Dataset estruturado em formato JSON com dados de ambiente, tempos, consumo de CPU/RAM/Disco e taxas de sucesso. |
| `README.md` | Este sumário executivo de auditoria de QA. |

A documentação detalhada com gráficos, tabelas e comparativos com o processo manual está publicada em [docs/15-metricas-desempenho.md](../../docs/15-metricas-desempenho.md).
