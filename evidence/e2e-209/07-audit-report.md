# Relatório de Auditoria KSC 16.x

## Pré-check
- **os_version** [OK]: SO suportado: rocky 9.8
- **selinux** [OK]: SELinux em modo 'enforcing'.
- **port_13000** [CRITICAL]: Porta 13000 em uso.
- **port_14000** [OK]: Porta 14000 livre.
- **port_443** [CRITICAL]: Porta 443 em uso.
- **ram_total** [WARNING]: RAM total 15732 MB abaixo da recomendação (16384 MB).
- **disk_opt** [OK]: Espaço em /opt (113 GB) adequado.
- **disk_varopt** [OK]: Espaço em /var/opt (113 GB) adequado.

## Pós-check
- **postgresql** [OK]: Ativo (postgresql-16).
- **klnagent_srv** [OK]: Ativo.
- **kladminserver_srv** [OK]: Ativo.
- **db_query** [OK]: SELECT 1 executado com sucesso.
- **web_console** [OK]: Porta 443 em LISTEN.
- **selinux** [OK]: SELinux em modo 'enforcing'.

## Evidências
Todos os logs e evidências brutos podem ser encontrados em: `evidence`
