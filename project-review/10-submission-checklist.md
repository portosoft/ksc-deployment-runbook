# 10. Checklist de revisão e de submissão

## 10.1 Checklist para o revisor da ferramenta principal

| Item de revisão | Status | Evidência | Observação |
|---|---|---|---|
| Objetivo do projeto está claro | ✅ | [00](00-executive-summary.md), [01](01-technical-overview.md) | — |
| Integração está documentada | ✅ | [03 §3.2](03-integration-with-main-tool.md) | Cada interface classificada por tipo |
| Uso de superfícies internas está declarado | ✅ | [03 §3.3](03-integration-with-main-tool.md) | Três pontos declarados abertamente |
| Compatibilidade foi testada | ❌ | — | **Declarada e inferida, nunca testada** (L-02) |
| Dependências estão identificadas | ✅ | `requirements.txt`, [01 §1.1](01-technical-overview.md) | Sem lockfile de árvore completa |
| Riscos de segurança foram avaliados | ⚠️ | [04](04-security-and-privacy.md) | Controles existem; auditoria externa nunca realizada |
| Testes principais existem | ⚠️ | 108 testes, 2026-09-12 | Somente unitários; nenhum E2E (L-02) |
| Limitações estão documentadas | ✅ | [06](06-known-limitations.md) | 15 limitações registradas |
| Processo de instalação está documentado | ✅ | `README.md`, `docs/03`–`docs/08` | Instalação efetiva ainda em mock (L-01) |
| Processo de contribuição está documentado | ✅ | `CONTRIBUTING.md`, `CODEOFCONDUCT.md` | — |
| Licença está definida | ✅ | Apache 2.0 | Sem redistribuição de artefatos Kaspersky |
| Rollback ou remoção estão documentados | ⚠️ | `docs/11-rollback.md` | Manual e nunca exercitado (L-06) |
| Solicitações aos mantenedores são objetivas | ✅ | [07 §7.1](07-collaboration-proposal.md), [08](08-maintainer-questions.md) | 5 pedidos, 7 perguntas |
| Aviso de não afiliação presente | ✅ | [README do pacote](README.md) | Sujeito a ajuste conforme Q7 |

Legenda: ✅ atendido · ⚠️ parcial · ❌ não atendido.

## 10.2 Checklist de submissão — a executar antes do envio

- [ ] R-03 concluído: `pytest -q` sem erros de coleta e cobertura publicada
- [ ] R-05 concluído: versão em inglês de `00`, `03` e do README
- [ ] R-10 iniciado: PRs duplicadas fechadas e agentes automatizados contidos
- [ ] Aviso de não afiliação presente no README do repositório, não apenas neste pacote
- [ ] Revisão final de que nenhum segredo real consta do repositório (`detect-secrets` verde)
- [ ] Confirmação de que nenhum artefato Kaspersky está versionado no repositório
- [ ] Canal de contato definido e verificado
- [ ] Destinatário correto identificado (canal de suporte, relações com comunidade ou equipe de produto Linux)
- [ ] Mensagem de [11-outreach-message.md](11-outreach-message.md) preenchida com nome, contato e repositório
- [ ] Uma pessoa externa ao projeto leu [00](00-executive-summary.md) e conseguiu descrever o que o projeto faz e o que ele ainda não faz

## 10.3 Classificação de prontidão

> **Pronto para discussão inicial e revisão técnica de arquitetura.**
> **Não pronto para piloto, submissão formal ou upstream.**

**Justificativa.**

Sustenta a classificação atual: a integração está mapeada e classificada por
tipo, as dependências frágeis estão declaradas em vez de omitidas, existe
suíte de testes unitários passando com 108 casos, controles de supply chain e
de segredos estão implementados e verificados em CI, a licença é clara e os
pedidos aos mantenedores são específicos e de baixo custo para eles. Há
material suficiente para uma conversa técnica produtiva.

Impede a classificação seguinte: nenhuma execução end-to-end em servidor real
foi realizada, quatro funções centrais de instalação permanecem como mocks, os
artefatos de evidência são de origem simulada, o rollback nunca foi exercitado
e não há nenhuma métrica de desempenho. Sem isso, qualquer afirmação de
compatibilidade seria especulação, e um piloto exporia usuários a um caminho
não comprovado.

**Gatilho para reclassificar como "pronto para piloto":** conclusão de R-01,
R-03, R-04 e R-06 do [backlog canônico](09-roadmap.md), com os logs reais
substituindo os artefatos simulados em `evidence/`.
