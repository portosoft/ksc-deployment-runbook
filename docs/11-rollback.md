# 11 - Rollback

## Objetivo
Retornar o host ao estado limpo se a instalação falhar de forma irrecuperável.

## Procedimento de Limpeza
1. **Remover Pacotes**:
   ```bash
   sudo dnf remove ksc64 ksc-web-console
   ```
2. **Remover Diretórios**:
   ```bash
   sudo rm -rf /opt/kaspersky /var/opt/kaspersky
   ```
3. **Limpar Banco de Dados**:
   ```sql
   DROP DATABASE ksc;
   DROP USER ksc_admin;
   ```

## Re-execução
Sempre reinicie o host após um rollback completo para limpar memória e descritores de arquivos.

---
[Próximo Passo: FAQ >>](12-faq.md)
