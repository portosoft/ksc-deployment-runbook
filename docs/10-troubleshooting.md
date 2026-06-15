# 10 - Troubleshooting

## Objetivo
Resolver falhas comuns de forma rápida e precisa.

## Tabela de Incidentes Comuns
| Sintoma | Causa Provável | Ação Corretiva |
| :--- | :--- | :--- |
| Falha ao iniciar `klserver` | `LD_LIBRARY_PATH` ausente. | Adicionar `export LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib` no `.bashrc`. |
| Erro de login no Web Console | Desincronização, porta OpenAPI fechada ou senha inválida. | Verficar porta 13299 e regras de senha (8-16 chars). |
| Falha de Autenticação (kscadmin) | Senha fora do padrão (max 16 chars) ou IAM desincronizado. | Redefinir senha complacente ou resetar IAM (veja abaixo). |

## Regras de Senha (Kaspersky Linux)
A Kaspersky impõe regras rígidas e silenciosas para senhas administrativas:
- **Tamanho**: Mínimo 8, MÁXIMO 16 caracteres.
- **Complexidade**: Pelo menos 3 grupos (Maiúsculas, Minúsculas, Números, Especiais).

## Habilitar OpenAPI (Porta 13299)
A porta OpenAPI não abre por padrão. Para habilitar:
```bash
sudo LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib \
  /opt/kaspersky/ksc64/sbin/klscflag -ssvset -pv klserver -s 87 \
  -n KLSRV_SP_OPEN_OAPI_PORT -sv true -svt BOOL_T \
  -ss '|ss_type = "SS_SETTINGS";'

sudo systemctl restart kladminserver_srv
```

## Correção de Porta no Web Console
Verifique se o `/var/opt/kaspersky/ksc-web-console/server/config.json` aponta para a porta **13299** no campo `port` dentro de `openAPIServers`.

## Procedimento kladduser (Fix Auth)
Se o login falhar no console web, certifique-se de usar uma senha de até 16 caracteres:
```bash
export LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib
sudo /opt/kaspersky/ksc64/sbin/kladduser -n KLAdmins -p <NOVA_SENHA_MAX_16>
```


## Coleta de Logs para Suporte
Sempre que abrir um ticket, anexe:
- `/var/log/kaspersky/ksc64/klserver.log`
- `/var/log/messages`
- Output do `kscctl audit --check`.

## Estudos de Caso de Troubleshooting (Histórico de Incidentes)

### Caso 1: Deadlock de Autenticação Multifator (MFA)
- **Sintoma**: Login via console web falha com `HTTP 401 Unauthorized` e cabeçalho `X-KSC-ErrorMsg: Two factor authentification configuration is forbidden`. O QR Code de configuração inicial não é exibido pela console.
- **Causa**: O parâmetro global `KLSRV_SP_MFA_ENABLED` está definido como `false` nas configurações do servidor, mas contas de administradores globais exigem o segundo fator internamente. A API OpenAPI rejeita a geração do segredo TOTP inicial porque a funcionalidade global de MFA está desativada.
- **Resolução**: Inserir uma exceção de MFA para a conta de administrador afetada diretamente no banco de dados e reiniciar os serviços:
  ```sql
  INSERT INTO mfa_totp_exceptions ("binId", "wstrName")
  SELECT "binId", "wstrName" FROM spl_users WHERE "wstrName" IN ('kscadmin');
  ```
  Reiniciar os serviços no servidor KSC:
  ```bash
  sudo systemctl restart kladminserver_srv kliam_srv ksc-web-console
  ```

### Caso 2: Falha de Inicialização do IAM pós-Migração
- **Sintoma**: O serviço `kliam_srv` não inicia devido a tabelas ausentes ou com inconsistência estrutural no schema `iam` após atualizações ou migrações do PostgreSQL.
- **Causa**: Inconsistências causadas por migrações marcadas como sujas (`schema_migrations.dirty` com valor `true`) ou corrupção de tabelas.
- **Resolução**: Parar os serviços, realizar o reset completo dos esquemas `ksc` e `ksciam` de forma controlada via CLI e reexecutar a reconfiguração:
  1. Executar o reset dos bancos:
     ```bash
     python3 -m automation.python.kscctl db reset --apply --confirm-token=RESET-CONFIRM
     ```
  2. Reexecutar a reconfiguração estruturada do serviço para reconstruir o banco PostgreSQL limpo:
     ```bash
     python3 -m automation.python.kscctl setup --apply
     ```

---
[Próximo Passo: Rollback >>](11-rollback.md)
