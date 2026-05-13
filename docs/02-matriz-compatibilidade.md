# 02 - Matriz de Compatibilidade

## Objetivo
Garantir que o hardware e o software escolhidos são oficialmente suportados pela Kaspersky e otimizados pelo time Portosoft.

## Sistemas Operacionais
| SO | Versão | Status |
| :--- | :--- | :--- |
| Rocky Linux | 9.2, 9.3, 9.4 | Suportado (Recomendado) |
| Oracle Linux | 9.x | Suportado (UEK ou RHCK) |
| AlmaLinux | 9.x | Compatível |

## Banco de Dados (PostgreSQL)
- **Versão**: 16.x (Suporte oficial KSC 16).
- **Nota**: Este runbook foca no PostgreSQL 16 instalado no mesmo host ou em host dedicado Linux.

## Dimensionamento (Sizing)
- **Pequeno (até 1000 hosts)**: 4 vCPU, 8GB RAM, 100GB SSD.
- **Médio (até 5000 hosts)**: 8 vCPU, 16GB RAM, 500GB SSD.

---
[Próximo Passo: Pré-requisitos >>](03-pre-requisitos.md)
