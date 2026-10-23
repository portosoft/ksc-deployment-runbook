# 6. Limitações conhecidas e riscos

## 6.1 Limitações

| # | Limitação | Categoria | Impacto | Quando ocorre | Mitigação atual | Solução planejada |
|---|---|---|---|---|---|---|
| ~~L-01~~ | **Resolvida.** Deploy real do KSC 16.3.0.1207 executado com sucesso em Rocky Linux 9.8 | — | — | — | — | [#209](https://github.com/portosoft/ksc-deployment-runbook/issues/209), concluída |
| ~~L-02~~ | **Mitigada.** Matriz ampliada com Oracle Linux 9 (UEK/RHCK) e KSC 16.2.0.1023 | Testes | — | — | Matriz de §3.5 e `docs/02` atualizadas com 3 combinações comprovadas e divergências documentadas | [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227), concluída |
| L-03 | Parte dos artefatos em `evidence/` ainda provém de execuções simuladas | Testes | Risco de leitura equivocada | Fora de `evidence/e2e-209/` | §5.4 distingue os dois conjuntos | — |
| L-04 | Dependência do esquema de `config.json` e `web-server.js` do Web Console | Compatibilidade | Quebra silenciosa em atualização do produto | Mudança de versão do KSC | Parsing JSON nativo em vez de regex | Q2 + [#207](https://github.com/portosoft/ksc-deployment-runbook/issues/207) |
| L-05 | **O instalador recusa reexecução do `postinstall.pl`**, caminho usado por `reconfigure_ksc_service.py` | Compatibilidade | Reconfiguração sem caminho suportado conhecido | Reconfiguração de servidor instalado | `setup --apply` detecta servidor configurado; a operação de reconfiguração segue apoiada nesse caminho | Q1 |
| L-06 | Sem rollback automático após falha parcial | Operação | Estado intermediário exige intervenção manual | Falha no meio do `--apply` | Procedimento manual em `docs/11-rollback.md` | [#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223) |
| ~~L-07~~ | **Resolvida.** Vault definido como padrão; `.env` rebaixado a modo degradado com aviso de segurança | — | — | — | — | [#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237), concluída |
| ~~L-08~~ | **Resolvida.** Sanitização ativa de segredos implementada em logging_utils (`SecretSanitizingFilter`, `set_redaction_secrets`) cobrindo `evidence/` e console | — | — | — | — | [#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237), concluída |
| ~~L-09~~ | **Resolvida.** Métricas completas de tempo (93s deploy / 14s reexecução), recursos e taxa de sucesso publicadas em `docs/15-metricas-desempenho.md` e `evidence/e2e-225/metrics.json` | — | — | — | — | [#225](https://github.com/portosoft/ksc-deployment-runbook/issues/225), concluída |
| L-16 | Portas divergem da documentação: a 13291 não escuta (a ativa é a **13299**) e a 14000 tampouco | Compatibilidade | Pré-checks e hardening miram portas erradas | Sempre | Divergência documentada em §3.3 | Q5 + [#205](https://github.com/portosoft/ksc-deployment-runbook/issues/205) |
| L-17 | O Web Console em porta privilegiada depende de um drop-in de capacidade sobre unidade gerada pelo instalador | Compatibilidade | Uma mudança na unidade pode invalidar o ajuste | `web_port` < 1024 | Drop-in próprio, sem editar a unidade original | Q2 |
| L-10 | Documentação exclusivamente em pt-BR | Documentação | Barreira para revisão internacional | Contato com equipe global | Este pacote identifica a lacuna | [#103](https://github.com/portosoft/ksc-deployment-runbook/issues/103) |
| ~~L-11~~ | **Resolvida.** Processo formal SemVer 2.0.0 em `VERSIONING.md`, empacotamento distribuível em `scripts/package_release.py` e `.github/workflows/release.yml` com manifesto `SHA256SUMS` e assinatura SSH | — | — | — | — | [#224](https://github.com/portosoft/ksc-deployment-runbook/issues/224), concluída |
| ~~L-12~~ | **Resolvida.** Pilha Ansible formalmente descontinuada via ADR-0001; 100% da orquestração unificada na CLI nativa Python (`kscctl`) | — | — | — | — | [#226](https://github.com/portosoft/ksc-deployment-runbook/issues/226), concluída |
| L-13 | Dois arquivos de teste fora de `tests/` quebram a coleta do pytest | Qualidade | Ruído na suíte; falso sinal de falha | Sempre | Conhecido e isolado | [#102](https://github.com/portosoft/ksc-deployment-runbook/issues/102) |
| L-14 | Sem suporte a alta disponibilidade, cluster ou múltiplos servidores | Escalabilidade | Escopo de servidor único | Sempre | Escopo declarado | Longo prazo |
| L-15 | Sem canal de suporte formal ou SLA | Suporte | Uso em produção por conta e risco do adotante | Sempre | `SECURITY.md` e issues do GitHub | [#224](https://github.com/portosoft/ksc-deployment-runbook/issues/224) |

## 6.2 Riscos que o projeto pode introduzir para a ferramenta principal

| Risco | Probabilidade | Impacto | Evidência | Mitigação | Responsável |
|---|---|---|---|---|---|
| Servidor mal configurado por dependência de arquivo interno alterado em nova versão | Média `[HIPÓTESE]` | Alto — Web Console inoperante | L-04 | Migrar para método suportado assim que indicado; declarar versão suportada por release | Projeto |
| Uso do `postinstall.pl` fora do contrato previsto | Média `[HIPÓTESE]` | Médio a alto | L-05 | Confirmação via Q1; caminho alternativo se houver | Projeto |
| Chamados de suporte à Kaspersky originados de ambientes automatizados por terceiros | Média `[HIPÓTESE]` | Médio — custo de suporte | Nenhuma | Relatório de auditoria identifica claramente que o deploy foi automatizado por este projeto; aviso de independência no README | Projeto |
| Confusão de marca / percepção de endosso oficial | Baixa | Médio | Nenhuma | Aviso explícito de não afiliação; disposto a ajustar o nome e a identidade visual conforme orientação | Projeto + Kaspersky (Q7) |
| Manipulação direta das bases `ksc`/`ksciam` causar estado inconsistente | Baixa a média `[HIPÓTESE]` | Alto | L-06 | Restrito a laboratório e a uma operação de suporte; sequência documentada | Projeto (Q4) |
| Divergência entre a documentação do projeto e a documentação oficial | Média | Médio | L-10 | Referenciar a documentação oficial como fonte primária e marcar o conteúdo próprio como complementar | Projeto |
| Incompatibilidade de licença | Baixa | Baixo | Apache 2.0; nenhum código ou pacote Kaspersky redistribuído | Nenhuma redistribuição de artefatos do produto | Projeto |
| Sobrecarga de requisições ao portal de pacotes | Baixa | Baixo | Download é opcional e sob demanda | Verificação local preferencial via `--verify-dir` | Projeto |

## 6.3 O que explicitamente **não** afirmamos

Para que a revisão parta de uma base honesta:

- Não afirmamos compatibilidade com o KSC 16.x em geral. Afirmamos que **uma
  combinação foi testada** — KSC 16.3.0.1207 em Rocky Linux 9.8 com PostgreSQL
  16 —, em uma única execução de laboratório. As demais seguem inferidas.
- Não afirmamos que o deploy automatizado é mais rápido, mais seguro ou mais
  confiável que o procedimento manual.
- Não afirmamos que o projeto está pronto para produção.
- Não afirmamos que o hardening proposto atende a qualquer norma ou framework
  de conformidade específico.
