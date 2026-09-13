# 4. Segurança e privacidade

Este documento descreve o que foi implementado, o que foi testado e,
principalmente, **o que ainda não foi avaliado**. O projeto não é declarado
seguro; ele é descrito com suas garantias e suas lacunas.

## 4.1 Dados processados

| Categoria | Exemplos | Onde reside | Tratamento |
|---|---|---|---|
| Credenciais de infraestrutura | Usuário/senha do PostgreSQL, conta administrativa do KSC, credenciais SSH | `configs/env/ksc_vars.env` ou vault local | Vault com cifragem local; `.env` em texto claro ainda é suportado `[LIMITAÇÃO]` |
| Identificadores de servidor | FQDN, IP, nome da base | `.env`, logs de evidência | Gravados nos logs de evidência |
| Dados operacionais | Estado de serviços, portas, parâmetros do PostgreSQL | `evidence/*/run.log` | Gravados em texto |
| Dados pessoais | **Nenhum coletado pelo projeto** | — | O projeto não lê inventário de endpoints nem dados de usuários geridos pelo KSC |

O projeto não envia telemetria e não comunica com nenhum serviço além do
servidor alvo e do portal oficial de pacotes Kaspersky, quando o download é
solicitado explicitamente. `[FATO]`

## 4.2 Controles implementados

| Controle | Implementação | Verificação |
|---|---|---|
| Cifragem de segredos em repouso | `automation/lib/vault.py` com `cryptography` | Testes unitários |
| Verificação de permissão da chave | `_assert_secure()` exige `0600` antes de ler `vault.key` | Teste unitário |
| Criação de arquivos sensíveis com modo restrito | `automation/python/utils/secure_file.py` | `tests/test_secure_file.py` |
| Integridade de artefatos (supply chain) | SHA-256 em blocos de 64 KB, comparação resistente a timing, gate obrigatório antes da instalação | `tests/test_packages.py` |
| Eliminação de credenciais realistas do repositório | Geração sintética em testes (`credentials.py`), marcadores `<PREENCHER>` nos `.example`, `.secrets.baseline` verificado em CI | `tests/test_credentials.py`, `tests/test_credentials_properties.py` (property-based com `hypothesis`) |
| Prevenção de injeção de comando | Substituição de `sed` por manipulação JSON nativa e por `ALTER SYSTEM`; `run_remote_sudo` centralizado em vez de `exec_command` direto | Revisão registrada em `docs/internal/review-remediation-v2.md` |
| Entrada hostil em testes | `generate_hostile_password()` produz senhas contendo `'`, espaço, `;`, `&` e `$(` | Testes de propriedade |
| Análise estática | CodeQL, Semgrep, Aikido e `detect-secrets` em CI | `.github/workflows/` |
| Hardening do alvo | Regras nftables para 443/8080/13000/13291/14000, permissões, SELinux | `docs/08-hardening.md`, `automation/bash/validate-harden.sh` |

## 4.3 Superfície de ataque e modelo de privilégio

O `kscctl` executa comandos com `sudo` no servidor alvo, através de SSH. Isso
significa que, na prática, **o host que roda o `kscctl` é um host privilegiado
em relação ao servidor KSC**. Consequências que o revisor deve considerar:

- Comprometimento do host de administração implica comprometimento do servidor
  KSC. Não há mitigação no projeto além do manuseio cuidadoso de segredos.
- Não há hoje um mapeamento mínimo de privilégios: não sabemos qual é o
  conjunto mínimo de comandos `sudo` necessário para cada operação. Solicitamos
  orientação a respeito (pergunta Q6).
- A verificação de host key do SSH e a política de `known_hosts` **não foram
  auditadas neste pacote**. `[NÃO VALIDADO]`

## 4.4 O que ainda não foi avaliado

| Item | Estado |
|---|---|
| Redação/sanitização de segredos nos logs de evidência | Não auditada sistematicamente `[NÃO VALIDADO]` |
| Política de verificação de host key SSH | Não auditada `[NÃO VALIDADO]` |
| Arquivos temporários de respostas enviados por SFTP para `/tmp` no alvo | Criados e usados; ciclo de vida e permissões não auditados `[LIMITAÇÃO]` |
| Assinatura de artefatos do próprio projeto | Inexistente — não há release assinada `[LIMITAÇÃO]` |
| Fixação (pinning) de dependências transitivas | `requirements.txt` fixa versões diretas; sem lockfile de árvore completa `[LIMITAÇÃO]` |
| Processo formal de resposta a incidentes | `SECURITY.md` define canal de reporte; sem SLA declarado |
| Teste de penetração ou revisão de segurança externa | Nunca realizado `[NÃO VALIDADO]` |

## 4.5 Divisão de responsabilidade de risco

| Risco | Origem | Observação |
|---|---|---|
| Manuseio de credenciais do operador | **Projeto** | Vault existe, mas `.env` em texto claro é permitido |
| Integridade dos pacotes instalados | **Compartilhado** | O projeto verifica; o catálogo depende das publicações oficiais |
| Segurança do produto instalado | **Ferramenta principal** | O projeto instala e aplica hardening documentado; não altera o produto |
| Configuração incorreta do Web Console por mudança de esquema | **Compartilhado** | Ver §3.3 e pergunta Q2 |
| Exposição de porta por regra nftables incorreta | **Projeto** | Regras revisadas; não validadas em ambiente real `[NÃO VALIDADO]` |

## 4.6 Recomendações que aplicaremos independentemente da revisão

1. Tornar o vault o caminho padrão e sinalizar o uso de `.env` em texto claro
   como modo degradado. ([#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237))
2. Implementar sanitização explícita de segredos na camada de log antes de
   qualquer promoção a piloto. ([#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237))
3. Auditar a política de host key do SSH e documentar o comportamento. ([#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237))
4. Documentar o conjunto mínimo de privilégios `sudo` por operação. ([#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237))
