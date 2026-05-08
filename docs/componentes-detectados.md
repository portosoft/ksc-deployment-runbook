# Inventário de Componentes Detectados

Este documento detalha os componentes do Kaspersky Security Center e dependências encontrados no servidor `kscserver` durante a auditoria de 2026-05-08.

## Pacotes Instalados (RPM)
- **PostgreSQL**: `postgresql-16.13` (Instalado e Ativo).
- **Kaspersky**: **NENHUM** pacote RPM da Kaspersky foi encontrado no banco de dados do RPM.
    - *Nota*: Indícios sugerem que foram desinstalados recentemente.

## Binários e Arquivos em Disco
- **PostgreSQL**: Localizado em `/usr/bin/postgres`.
- **Arquivos de Instalação (Cache/Home)**:
    - `/home/***REMOVED***/ksc64-16.2.0-1023.x86_64.rpm` (Instalador Server).
    - `/tmp/klnagent64-16.2.0-1023.x86_64.rpm` (Instalador Agente).
    - `/tmp/ksc-web-console-16.2.11309.x86_64.rpm` (Instalador Web Console).

## Diretórios de Dados
- `/opt/kaspersky`: **Inexistente**.
- `/var/opt/kaspersky`: **Inexistente** (apesar de haver processo órfão referenciando este caminho).
- `/var/lib/pgsql/data`: Ativo (Dados do PostgreSQL).

## Processos Ativos e Órfãos
- **PostgreSQL 16**: Rodando normalmente (PID 17927).
- **KSC Web Console**: Processo órfão detectado (PID 40080).
    - Executável: `/var/opt/kaspersky/ksc-web-console/node` (**DELETED**).
    - Diretório: `/var/opt/kaspersky/ksc-web-console` (**DELETED**).
    - *Conclusão*: O serviço está rodando apenas em memória; os arquivos em disco foram removidos.
- **NATS Server**: Rodando (PID 41222).

## Evidências de Desinstalação
- Arquivo detectado: `/tmp/klnagent_srv_uninstall-wd.log`.
- Data da desinstalação: **2026-05-05**.

---
*Auditoria realizada por Antigravity em 2026-05-08.*
