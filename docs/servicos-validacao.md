# Validação de Serviços Systemd

Status dos serviços relacionados ao KSC e Banco de Dados em 2026-05-08.

| Serviço | Nome Systemd | Status Real | Observação |
| :--- | :--- | :--- | :--- |
| **PostgreSQL 16** | `postgresql` | **Ativo e Saudável** | Rodando na porta 5432. |
| **KSC Server** | `kladminserver_srv` | **Ausente** | Unit file não encontrado / Pacote removido. |
| **KSC Web Console** | `ksc-web-console` | **Inativo (Dead)** | Unit file existe, mas processo real é órfão. |
| **Identity & Access** | `kliam_srv` | **Ausente** | Unit file não encontrado. |
| **Network Agent** | `klnagent` | **Ausente** | Marcado como `not-found`. |

## Diagnóstico de Processos (ps)
- O processo do **PostgreSQL** é o único componente persistente e válido.
- O processo do **KSC Web Console** (Node.js) deve ser finalizado antes de uma nova instalação, pois seus arquivos em disco foram deletados e ele reside apenas em memória.

## Ação Recomendada
1. Matar o processo órfão do Web Console.
2. Proceder com a reinstalação dos pacotes RPM disponíveis em `/home/suporte`.

---
*Auditoria realizada por Antigravity em 2026-05-08.*
