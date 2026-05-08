# Matriz de Progresso - Auditoria kscserver

Estado real da implantação após auditoria operacional de 2026-05-08.

| Item | Status | Evidência | Ação Necessária |
| :--- | :--- | :--- | :--- |
| **Hostname Final** | Concluído | `hostnamectl` mostra `kscserver` | Nenhuma. |
| **PostgreSQL Instalado** | Concluído | RPM `postgresql-16` presente | Nenhuma. |
| **PostgreSQL Ativo** | Concluído | `systemctl status postgresql` | Nenhuma. |
| **`standard_conforming_strings = on`** | Concluído | `SHOW` no psql retorna `on` | Nenhuma. |
| **Banco KSC Presente** | **Pendente** | `\l` não mostra banco `ksc` | Criar no setup do KSC. |
| **Banco IAM Presente** | **Pendente** | `\l` não mostra banco `ksciam` | Criar no setup do KSC. |
| **Pacotes KSC Instalados** | **Inconsistente** | `rpm -qa` não mostra pacotes | Reinstalar via RPM local. |
| **Pós-instalação Concluído** | **Pendente** | Arquivos em `/opt` ausentes | Rodar `postinstall.pl` após instalação. |
| **Usuário Admin KSC** | **Pendente** | Banco de dados ausente | Criar no setup inicial. |
| **`kladminserver_srv` Ativo** | **Pendente** | Serviço não encontrado | Instalar pacote Server. |
| **`klwebsrv_srv` Ativo** | **Inconsistente** | Processo órfão detectado | Matar processo e reinstalar. |
| **`kliam_srv` Ativo** | **Pendente** | Serviço não encontrado | Instalar pacote Console. |
| **Portas Coerentes** | **Parcial** | Apenas 5432 e 4222 em escuta | Aguardar instalação dos serviços. |
| **Firewall Coerente** | Concluído | Portas 13000, 13001, 8443 abertas | Nenhuma (já estão prontas). |
| **Web Console Acessível** | **Pendente** | Porta 8443 não responde | Reinstalar Web Console. |

## Resumo Executivo
O servidor está "limpo" de binários e dados do KSC, mas com a infraestrutura de suporte (PostgreSQL e Firewall) configurada corretamente. A implantação deve ser retomada do passo de **Instalação do Pacote KSC Server**.

---
*Matriz gerada por Antigravity em 2026-05-08.*
