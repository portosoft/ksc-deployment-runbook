# 10. Checklist de revisão e de submissão

## 10.1 Checklist para o revisor da ferramenta principal

| Item de revisão | Status | Evidência | Observação |
|---|---|---|---|
| Objetivo do projeto está claro | ✅ | [00](00-executive-summary.md), [01](01-technical-overview.md) | — |
| Integração está documentada | ✅ | [03 §3.2](03-integration-with-main-tool.md) | Cada interface classificada por tipo |
| Uso de superfícies internas está declarado | ✅ | [03 §3.3](03-integration-with-main-tool.md) | Três pontos declarados abertamente |
| Compatibilidade foi testada | ⚠️ | `evidence/e2e-209/`, 2026-09-12 | KSC 16.3.0.1207 + Rocky 9.8 + PG 16 testado; demais combinações inferidas (L-02) |
| Dependências estão identificadas | ✅ | `requirements.txt`, [01 §1.1](01-technical-overview.md) | Sem lockfile de árvore completa |
| Riscos de segurança foram avaliados | ⚠️ | [04](04-security-and-privacy.md) | Controles existem; auditoria externa nunca realizada. O E2E revelou que o hardening derrubava o produto — corrigido e coberto por teste |
| Testes principais existem | ✅ | 144 testes + ciclo E2E completo | Cobertura percentual ainda não publicada |
| Limitações estão documentadas | ✅ | [06](06-known-limitations.md) | 15 limitações registradas |
| Processo de instalação está documentado | ✅ | `README.md`, `docs/03`–`docs/08`, `docs/14` | Instalação exercitada com sucesso em servidor real |
| Processo de contribuição está documentado | ✅ | `CONTRIBUTING.md`, `CODEOFCONDUCT.md` | — |
| Licença está definida | ✅ | Apache 2.0 | Sem redistribuição de artefatos Kaspersky |
| Rollback ou remoção estão documentados | ⚠️ | `docs/11-rollback.md` | Manual e nunca exercitado — [#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223) (L-06) |
| Solicitações aos mantenedores são objetivas | ✅ | [07 §7.1](07-collaboration-proposal.md), [08](08-maintainer-questions.md) | 5 pedidos, 7 perguntas |
| Aviso de não afiliação presente | ✅ | [README do pacote](README.md) | Sujeito a ajuste conforme Q7 |

Legenda: ✅ atendido · ⚠️ parcial · ❌ não atendido.

## 10.2 Checklist de submissão — a executar antes do envio

- [x] Validação E2E concluída ([#209](https://github.com/portosoft/ksc-deployment-runbook/issues/209)) com evidências em `evidence/e2e-209/`
- [ ] [#102](https://github.com/portosoft/ksc-deployment-runbook/issues/102) concluído: `pytest -q` sem erros de coleta e cobertura publicada
- [ ] [#103](https://github.com/portosoft/ksc-deployment-runbook/issues/103) concluído: versão em inglês de `00`, `03` e do README
- [ ] [#229](https://github.com/portosoft/ksc-deployment-runbook/issues/229) iniciado: PRs duplicadas fechadas e agentes automatizados contidos
- [ ] Aviso de não afiliação presente no README do repositório, não apenas neste pacote
- [ ] Revisão final de que nenhum segredo real consta do repositório (`detect-secrets` verde)
- [ ] Confirmação de que nenhum artefato Kaspersky está versionado no repositório
- [ ] Canal de contato definido e verificado
- [ ] Destinatário correto identificado (canal de suporte, relações com comunidade ou equipe de produto Linux)
- [ ] Mensagem de [11-outreach-message.md](11-outreach-message.md) preenchida com nome, contato e repositório
- [ ] Uma pessoa externa ao projeto leu [00](00-executive-summary.md) e conseguiu descrever o que o projeto faz e o que ele ainda não faz

## 10.3 Classificação de prontidão

> **Pronto para revisão técnica.**
> **Não pronto para piloto, submissão formal ou upstream.**

**Justificativa.**

Sustenta a classificação atual: o ciclo completo foi executado contra um KSC
16.3.0.1207 real em Rocky Linux 9.8, com `setup --apply` concluindo em 0, Web
Console respondendo em HTTPS e relatório de auditoria sem falhas críticas. A
integração está mapeada e classificada por tipo, as dependências frágeis estão
declaradas em vez de omitidas, há 144 testes unitários passando somados à
evidência E2E, e os controles de supply chain e de segredos são verificados em
CI. Os dez defeitos que a execução real revelou foram corrigidos e cobertos por
testes de regressão.

Impede a classificação seguinte: a matriz tem **uma única combinação testada**,
em uma **única execução de laboratório**; o rollback nunca foi exercitado
([#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223)); a idempotência foi tratada no código mas não medida
([#228](https://github.com/portosoft/ksc-deployment-runbook/issues/228)); não há nenhuma métrica de desempenho ([#225](https://github.com/portosoft/ksc-deployment-runbook/issues/225)); e o
`.env` em texto claro continua sendo caminho suportado ([#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237)). Um
piloto exporia usuários a caminhos de recuperação que nunca foram exercitados.

**Gatilho para reclassificar como "pronto para piloto":** conclusão de
[#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223), [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227), [#228](https://github.com/portosoft/ksc-deployment-runbook/issues/228) e [#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237).
Acompanhamento no [board](https://github.com/orgs/portosoft/projects/1).
