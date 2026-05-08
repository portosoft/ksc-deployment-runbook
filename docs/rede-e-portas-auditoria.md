# Auditoria de Rede e Portas

Mapeamento de portas abertas, serviços em escuta e conectividade.

## Portas em Escuta (ss -tlnp)
| Porta | IP/Bind | Processo (PID) | Serviço |
| :--- | :--- | :--- | :--- |
| **22** | `0.0.0.0` | `840` | `sshd` |
| **5432** | `127.0.0.1` | `17927` | `postgres` |
| **4222** | `*` | `41222` | `nats-server` |

*Nota: As portas 8080, 8443, 13000 e 13001 **NÃO** estão em escuta no momento.*

## Configuração de Firewall (firewalld)
As seguintes portas estão abertas no firewall, apesar de não haver serviços escutando em todas:
- **TCP**: 13000, 13001, 8080, 8443, 8060, 8061.
- **Serviços padrão**: `ssh`, `cockpit`, `dhcpv6-client`.

## Inconsistência Detectada
- O firewall está permitindo tráfego para portas do KSC (13000, 13001, 8443), mas o servidor KSC não está instalado/rodando para processar essas requisições.
- O acesso ao PostgreSQL (5432) está limitado ao `localhost`. Caso o KSC seja instalado em outro host (o que não é o caso atual), o bind precisaria ser alterado.

## Resposta Local (Curl)
- `http://127.0.0.1:8080`: **Falha** (Conexão recusada).
- `https://127.0.0.1:8443`: **Falha** (Conexão recusada).
- *Obs*: O processo órfão do Web Console não parece estar respondendo corretamente ou sua porta não está mapeada no `ss`.

---
*Auditoria realizada por Antigravity em 2026-05-08.*
