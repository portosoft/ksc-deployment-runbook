# Relatório de Auditoria KSC 16.x

## Pré-check
Não aplicável: o KSC já está instalado neste servidor. As verificações de pré-instalação avaliam condições de partida, como portas livres, que deixam de valer depois do deploy.

## Pós-check
- **postgresql** [OK]: Ativo (postgresql-16).
- **klnagent_srv** [OK]: Ativo.
- **kladminserver_srv** [OK]: Ativo.
- **db_query** [OK]: SELECT 1 executado com sucesso.
- **web_console** [OK]: Porta 443 em LISTEN.
- **selinux** [OK]: SELinux em modo 'enforcing'.

## Resumo
Nenhuma falha crítica no pós-check.

## Evidências
Todos os logs e evidências brutos podem ser encontrados em: `evidence`
