# Troubleshooting (Resolução de Problemas)

Guia de referência para resolver problemas comuns encontrados durante a implantação e operação do KSC 16.x no Linux.

## 1. Web Console não abre (Porta 8443)
**Sintomas**: O navegador retorna "Conexão Recusada" ou timeout ao acessar a porta 8443.

- **Causa 1**: Serviço `klwebsrv_srv` parado.
    - **Ação**: `sudo systemctl restart klwebsrv_srv`.
- **Causa 2**: Firewall bloqueando a porta.
    - **Ação**: Verifique com `sudo firewall-cmd --list-ports`. Adicione se faltar.
- **Causa 3**: Falha no serviço IAM (`kliam_srv`).
    - **Ação**: Verifique os logs em `/var/log/kaspersky/ksc64/kliam_srv.log`.

## 2. Erro de Banco de Dados no Post-Install
**Sintomas**: O script `postinstall.pl` falha ao tentar conectar ou criar tabelas no PostgreSQL.

- **Causa 1**: Parâmetro `standard_conforming_strings` em `off`.
    - **Ação**: Altere para `on` no `postgresql.conf` e reinicie o serviço.
- **Causa 2**: Permissões no `pg_hba.conf`.
    - **Ação**: Garanta que o método de conexão para o host local seja `trust` ou `md5` com a senha correta.
- **Causa 3**: PostgreSQL não está rodando.
    - **Ação**: `systemctl status postgresql-16`.

## 3. Agentes não conectam (Porta 13000)
**Sintomas**: Computadores aparecem como "Desconectados" na console.

- **Causa 1**: Hostname do servidor mudou ou não resolve.
    - **Ação**: Use o utilitário `klmover` no cliente para apontar para o IP/FQDN correto.
- **Causa 2**: Porta 13000/tcp fechada no servidor.
    - **Ação**: Teste a conectividade a partir do cliente: `telnet [IP-SERVER] 13000`.

## 4. Consumo excessivo de memória/CPU
**Sintomas**: O servidor fica lento e os serviços do KSC consomem muitos recursos.

- **Causa**: PostgreSQL mal dimensionado.
    - **Ação**: Execute o `VACUUM ANALYZE` no banco de dados e revise as configurações de memória (`shared_buffers`, `work_mem`) no `postgresql.conf`.

## Comandos Úteis de Diagnóstico
- **Logs globais**: `journalctl -u kladminserver_srv`
- **Portas em escuta**: `ss -tlnp | grep -E '8443|13000|13001'`
- **Status do DB**: `sudo -u postgres psql -c "select pg_is_in_recovery();"`
