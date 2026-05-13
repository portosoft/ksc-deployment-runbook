# 02 - Instalação do Administration Server

Este guia cobre a limpeza total do servidor e a instalação do componente principal (KSC Server).

## Fase 0: Limpeza Total

Antes de qualquer instalação, execute os comandos de limpeza:

```bash
# Parar e desabilitar serviços
sudo systemctl stop KSCWebConsole.service KSCSvcWebConsole.service kladminserver_srv klnagent_srv kliam_srv 2>/dev/null || true
sudo systemctl disable KSCWebConsole.service KSCSvcWebConsole.service kladminserver_srv klnagent_srv kliam_srv 2>/dev/null || true

# Remover pacotes
sudo rpm -e ksc-web-console ksc64 klnagent64 --nodeps 2>/dev/null || true

# Limpar disco e banco
sudo rm -rf /opt/kaspersky /var/opt/kaspersky /etc/opt/kaspersky
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ksc;"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ksciam;"
sudo -u postgres psql -c "DROP ROLE IF EXISTS kluser;"
```

## Fase 1: Instalação do Servidor

1. **Instalar Network Agent**:
   ```bash
   sudo rpm -ivh klnagent64-16.2.0-1023.x86_64.rpm
   ```

2. **Instalar KSC Server**:
   ```bash
   sudo rpm -ivh ksc64-16.2.0-1023.x86_64.rpm
   ```

3. **Configuração Pós-instalação (Interativa)**:
   ```bash
   sudo LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl
   ```
   **Parâmetros recomendados:**
   - DB Type: PostgreSQL
   - Host: 127.0.0.1
   - Port: 5432
   - DB Names: ksc / ksciam
   - DB User: kluser
   - Service Account: ksc
   - Group: kladmins
