# Configuração do Banco de Dados (PostgreSQL 16)

O Kaspersky Security Center 16.x no Linux utiliza o PostgreSQL como seu motor de dados principal. Esta seção detalha a preparação crítica necessária.

## Por que PostgreSQL 16?
- **Performance**: Melhor gerenciamento de conexões e performance de I/O em relação a versões anteriores.
- **Suporte**: Alinhamento com as versões mais recentes suportadas pela Kaspersky.
- **Open Source**: Facilidade de manutenção e custo zero de licenciamento.

## Ajustes Críticos no PostgreSQL

### 1. Parâmetro `standard_conforming_strings`
O instalador do KSC falhará se este parâmetro não estiver definido como `on`.
- Verifique no arquivo `/var/lib/pgsql/data/postgresql.conf` (ou similar):
  ```conf
  standard_conforming_strings = on
  ```

### 2. Autenticação (`pg_hba.conf`)
Garanta que o usuário do KSC consiga se conectar localmente.
- Exemplo de configuração recomendada em `/var/lib/pgsql/data/pg_hba.conf`:
  ```text
  # TYPE  DATABASE        USER            ADDRESS                 METHOD
  local   all             all                                     trust
  host    all             all             127.0.0.1/32            md5
  ```

## Estrutura Lógica
Durante a instalação, o KSC criará (ou solicitará a criação de) dois bancos de dados:
1. **Banco KSC**: Armazena dados do Administration Server.
2. **Banco IAM**: Armazena dados do Identity and Access Management.

## Comandos de Validação
Use o `psql` para validar se o PostgreSQL está pronto:

```bash
# Verificar versão
psql --version

# Verificar se o serviço está rodando
systemctl status postgresql-16

# Validar parâmetro crítico
sudo -u postgres psql -c "SHOW standard_conforming_strings;"
```

O resultado do comando `SHOW` deve ser obrigatoriamente `on`.

## Backup e Manutenção
- Recomenda-se o uso de `pg_dump` para backups regulares.
- O KSC possui uma tarefa interna de backup, mas o backup a nível de DB é uma camada extra de segurança.
