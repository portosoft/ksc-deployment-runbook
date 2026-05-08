# Auditoria do Banco de Dados (PostgreSQL 16)

Detalhes do estado do PostgreSQL e bancos de dados para o KSC.

## Estado do Motor (PostgreSQL 16)
- **Status**: Rodando.
- **Porta**: 5432 (TCP).
- **Bind**: `127.0.0.1` e `::1` (Acesso apenas local).

## Configurações Críticas
| Parâmetro | Valor Atual | Status |
| :--- | :--- | :--- |
| `standard_conforming_strings` | `on` | **OK** (Correto para KSC) |
| `hba_file` | `/var/lib/pgsql/data/pg_hba.conf` | - |
| `config_file` | `/var/lib/pgsql/data/postgresql.conf` | - |

## Inventário de Bancos e Roles
- **Bancos Existentes**: `postgres`, `template0`, `template1`.
- **Bancos KSC/IAM**: **NÃO ENCONTRADOS**.
    - Os bancos `ksc` e `ksciam` foram deletados.
- **Roles**: Apenas a role `postgres` (Superusuário) está presente.
    - Roles específicas do KSC (ex: `kscadmin`, `kscdbuser`) foram removidas.

## Conclusão
O PostgreSQL está pronto para receber uma nova instalação do KSC (parâmetros de string corretos), mas todos os dados de instalações anteriores foram removidos.

---
*Auditoria realizada por Antigravity em 2026-05-08.*
