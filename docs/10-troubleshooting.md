# 10 - Troubleshooting

## Objetivo
Resolver falhas comuns de forma rápida e precisa.

## Tabela de Incidentes Comuns
| Sintoma | Causa Provável | Ação Corretiva |
| :--- | :--- | :--- |
| Falha ao iniciar `klserver` | `LD_LIBRARY_PATH` ausente. | Adicionar `export LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib` no `.bashrc`. |
| Erro de login no Web Console | Desincronização de certificados. | Reiniciar `klwebsrv`. |
| Conexão com banco falha | `DBMS_TYPE` incorreto no arquivo de respostas. | Garantir que o valor seja `Postgres`. |
| Instalação trava em "Creating DB" | Falha de permissão no Postgres. | Verificar `pg_hba.conf` e se o usuário tem privilégios de `SUPERUSER`. |

## Coleta de Logs para Suporte
Sempre que abrir um ticket, anexe:
- `/var/log/kaspersky/ksc64/klserver.log`
- `/var/log/messages`
- Output do `ksc_audit.py --check`.

---
[Próximo Passo: Rollback >>](11-rollback.md)
