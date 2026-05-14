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
- Output do `ksc_audit.py --check`.

---
[Próximo Passo: Rollback >>](11-rollback.md)
