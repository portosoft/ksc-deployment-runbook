# 01 - Pré-requisitos do Sistema

Para a instalação correta do Kaspersky Security Center 16.2 no Linux (Rocky Linux 9.7), os seguintes componentes devem estar ativos e configurados:

## Sistema Operacional
- **OS**: Rocky Linux 9.7 ou compatível.
- **Hostname**: Configurado corretamente (Ex: `FQDN_AQUI`).
- **SELinux**: Recomenda-se modo `Permissive` ou `Enforcing` com as políticas corretas aplicadas.

## Banco de Dados (PostgreSQL 16)
- **Status**: Ativo na porta 5432.
- **Configuração**: Deve permitir conexões locais do usuário `postgres`.
- **Limpeza**: Antes de iniciar, garanta que não existam bancos `ksc` ou `ksciam` remanescentes de instalações anteriores.

## Usuários e Grupos
- **Usuário de serviço**: `ksc`
- **Grupo de segurança**: `kladmins`
- O usuário `ksc` deve pertencer ao grupo `kladmins`.

## Arquivos RPM necessários
Localizados em `/home/USUARIO_AQUI/`:
1. `ksc64-16.2.0-1023.x86_64.rpm`
2. `klnagent64-16.2.0-1023.x86_64.rpm`
3. `ksc-web-console-16.2.11309.x86_64.rpm`
