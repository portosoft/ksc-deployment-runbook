# KSC 16.2 Error Remediation Log

## [STATUS ATUAL] - Investigação de Inconsistência de Dados (DB Ghosting)

---

## 1. Erro de Lockout por MFA Incompleto (BLOQUEANTE)
- **Status:** Em andamento.
- **Erro:** Usuário administrativo correto, mas bloqueado por exigência de segundo fator não configurado.
- **Diagnóstico:** O 2FA foi habilitado via banco/política, mas o processo de configuração inicial (TOTP) nunca foi concluído.
- **Remediação Tentada:**
    - Purga das tabelas `authentication_factors` no banco `ksciam`.
    - Desativação da flag global `KLSRV_SP_MFA_ENABLED` via `klscflag` (SUCESSO na desativação, mas lockout persiste).
- **Pendência:** Identificar por que o serviço IAM ainda exige MFA mesmo com tabelas vazias.

## 2. Desaparecimento de Tabelas no Banco ksciam (CRÍTICO)
- **Status:** Não solucionado.
- **Erro:** O esquema `iam` reduziu de 53 tabelas para 17 tabelas.
- **Diagnóstico:** Tabelas vitais como `authentication_factors` e `identities` não são mais encontradas pelo Postgres (`relation does not exist`).
- **Impacto:** O serviço de identidade (IAM) está operando em estado degradado ou desinicializado.

## 3. Discrepância de Provisionamento (User Creation Ghosting)
- **Status:** Não solucionado.
- **Erro:** O comando `kladduser` afirma que o usuário foi criado com sucesso, mas as tabelas `ak_users` (banco `ksc`) e `accounts` (banco `ksciam`) permanecem com zero linhas.
- **Diagnóstico:**
    - O banco `ksc` possui 113 MB de dados, mas as tabelas auditadas aparecem vazias.
    - Reinício do serviço `kladminserver_srv` não forçou a sincronização dos dados.
- **Hipótese:** Uso de esquemas não padrão ou redirecionamento de escrita via proxy interno do Kaspersky.

## 4. Falha de Conectividade do Kaspersky Web Console
- **Status:** Solucionado parcialmente.
- **Erro:** "Authentication failed" genérico na interface web.
- **Remediação:** Verificação de portas e serviços (IAM porta 9500, Web Console porta 8080). Confirmado que o backend está acessível, mas rejeita credenciais devido ao estado do banco de dados.

---
**Próximos Passos:**
1. Localizar a porta física de escuta do Postgres (conflito entre `ss` e conectividade real).
2. Forçar a re-inicialização do esquema IAM.
3. Tentar login via API bypassando a interface Web para capturar erros brutos.
