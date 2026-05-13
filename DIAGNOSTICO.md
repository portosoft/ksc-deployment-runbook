# DIAGNÓSTICO EXECUTIVO: KSC Deployment Runbook

## 1. Visão Geral do Estado Atual
O repositório `portosoft/ksc-deployment-runbook` possui uma fundação técnica sólida em termos de scripts Python e documentação técnica, mas falha gravemente na **orquestração da jornada do usuário**. Atualmente, o projeto assemelha-se a um "depósito de scripts e notas de instalação" em vez de um runbook operacional executável. A presença de múltiplos scripts de debug soltos e documentação duplicada gera ruído e reduz a confiabilidade necessária para um ambiente de produção.

## 2. Forças Reais do Projeto
- **Scripts Python Funcionais**: Os scripts `ksc_setup.py` e `ksc_harden_db.py` demonstram conhecimento profundo dos parâmetros de instalação do Kaspersky.
- **Troubleshooting Baseado em Experiência**: As notas sobre `LD_LIBRARY_PATH` e `SELinux` são críticas e salvam horas de depuração.
- **Escopo Definido**: O projeto foca corretamente no stack Rocky/Oracle Linux 9 + PostgreSQL 16.

## 3. Falhas Críticas
| Problema | Impacto | Evidência | Correção Recomendada |
| :--- | :--- | :--- | :--- |
| **Caos na Pasta Automation** | Operador não sabe qual script rodar primeiro ou quais são apenas para debug. | 60+ scripts soltos em `automation/`. | Consolidar scripts em um toolkit padronizado e mover auxiliares para `archive/`. |
| **Documentação Duplicada/Desatualizada** | Risco de seguir instruções obsoletas. | `docs/01-prerequisitos.md` vs `docs/prerequisitos.md`. | Adotar numeração estrita e única para a jornada do operador (00-12). |
| **Falta de Validação Pré-Execução** | Setup falha no meio do processo por falta de pré-requisitos simples. | Scripts de instalação não executam pre-checks obrigatórios de DNS/DB. | Implementar flag `--check` obrigatória em todos os scripts principais. |
| **Naming Ambíguo de Scripts** | Perda de tempo tentando entender o que é "final_fix" ou "final_attempt". | `ksc_final_attempt.py` e `ksc_final_setup.py`. | Remover versões "final", "fix" e manter apenas o script canônico versionado. |

## 4. Falhas Moderadas
| Problema | Impacto | Evidência | Correção Recomendada |
| :--- | :--- | :--- | :--- |
| **CI Ineficiente** | Scripts com erros de sintaxe ou links quebrados podem passar. | `ci.yml` valida apenas 1 arquivo específico. | Expandir CI para cobrir todos os scripts (lint) e validar integridade do Markdown. |
| **Contrato de Configuração Frágil** | Variáveis de ambiente e arquivos `.env` não estão sincronizados. | `ksc_vars.env.example` não cobre todos os parâmetros dos scripts. | Criar um documento de "Contrato Operacional" ligando envs a parâmetros. |

## 5. Riscos Operacionais
- **Risco de Segurança**: Arquivos `.bin` e `.key` em `configs/` podem conter segredos reais ou confundir o operador sobre onde armazenar credenciais.
- **Risco de Rollback**: Não há procedimento claro de reversão se a instalação do banco de dados ou do KSC falhar parcialmente.
- **Risco de Dependência de Conhecimento Tácito**: A "mágica" para o Web Console funcionar está espalhada em 10+ scripts de `fix_web_*.py` em vez de um workflow único.

## 6. Por que o projeto não entrega plenamente?
O projeto entrega **componentes**, mas não entrega um **processo**. Um operador de nível júnior/pleno terá dificuldades em conectar os scripts de automação com os passos manuais descritos na documentação, aumentando a chance de erro humano e inconsistência entre servidores.

---
**Status da Auditoria:** Concluída (Nível Severo)
**Recomendação:** Refatoração Estrutural Imediata.
