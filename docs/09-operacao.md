# 09 - Operação

## Objetivo
Manter a saúde do KSC após o deploy.

## Backup
O backup do KSC deve ser feito via utilitário `klbackup`.
```bash
/opt/kaspersky/ksc64/sbin/klbackup -path /backup/ksc -password <senha>
```
**Nota**: Configure um cronjob para realizar este backup diariamente.

## Atualização de Patches
1. Pare os serviços: `systemctl stop klserver klwebsrv`.
2. Instale o novo RPM.
3. Inicie os serviços.

---
[Próximo Passo: Troubleshooting >>](10-troubleshooting.md)
