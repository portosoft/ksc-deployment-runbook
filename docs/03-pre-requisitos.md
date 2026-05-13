# 03 - Pré-requisitos

## Objetivo
Preparar o terreno antes de iniciar qualquer script de instalação.

## Checklist de Infraestrutura
- [ ] **Hostname**: Deve ser um FQDN válido (ex: `ksc01.empresa.local`).
- [ ] **DNS**: Resolução direta e reversa configurada.
- [ ] **Internet**: Acesso aos repositórios Rocky/Oracle e Kaspersky.
- [ ] **Repositórios**: `epel-release` instalado.

> [!IMPORTANT]
> A resolução DNS é o ponto onde 80% das falhas de instalação ocorrem. Certifique-se de que o comando `hostname -f` retorna o FQDN correto.

## Liberação de Portas (Firewall Interno)
| Porta | Protocolo | Origem | Destino | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| 443 | TCP | Admin | KSC Server | Console Web |
| 13000 | TCP | Endpoints | KSC Server | SSL Agent Comm |
| 14000 | TCP | Endpoints | KSC Server | Non-SSL Agent Comm |
| 13291 | TCP | Localhost | KSC Server | API Administrativa |

> [!WARNING]
> Se o PostgreSQL for instalado em um servidor remoto, a porta **5432/TCP** deve estar liberada entre o KSC Server e o DB Server.

## Usuário
- O operador deve ter privilégios de `sudo` total.

---
[Próximo Passo: Precheck >>](04-precheck.md)
