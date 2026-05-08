# Auditoria de Logs e Saúde

Resumo de evidências de saúde coletadas dos logs do sistema e instaladores.

## Status Geral dos Logs
- **Systemd Journal**: Estável, sem erros críticos de hardware ou kernel. Muitos registros de sessões SSH e `sudo` devido à auditoria atual.
- **Logs de Instalação**:
    - `/tmp/ksc64_install.log`: Registra uma tentativa de instalação passada.
    - `/tmp/klnagent_srv_uninstall-wd.log`: **CRÍTICO**. Registra a desinstalação bem-sucedida do Network Agent em 05/05/2026.

## Erros e Alertas Detectados
1. **Processo Órfão (Zombie)**:
    - O processo `node ./index.js` (PID 40080) está rodando sem os arquivos correspondentes em `/var/opt/kaspersky`. Isso gerará erros de E/S caso o processo tente ler qualquer arquivo de configuração ou log.
2. **PostgreSQL**:
    - Log do Postgres mostra tentativas falhas de conexão ao banco `ksc` e `ksciam` (geradas pela nossa auditoria), confirmando que os bancos não existem mais.

## Evidência de Saúde dos Serviços
- **PostgreSQL**: **Saudável**. O motor está pronto para uso.
- **KSC**: **Inexistente**. Requer nova implantação.

---
*Auditoria realizada por Antigravity em 2026-05-08.*
