# Pacote de Revisão Técnica — KSC Deployment Runbook

Este diretório contém o material preparado para avaliação técnica do projeto
**KSC Deployment Runbook** por desenvolvedores, mantenedores e engenheiros da
**ferramenta principal: Kaspersky Security Center 16.x (distribuição Linux)**.

O pacote descreve como o projeto utiliza o KSC, quais interfaces consome, que
evidências existem, quais limitações permanecem em aberto e o que está sendo
solicitado à equipe da Kaspersky.

## Como ler este pacote

| Perfil do leitor | Comece por |
|---|---|
| Gestor técnico / Product Manager | [00-executive-summary.md](00-executive-summary.md) |
| Arquiteto de soluções | [02-architecture.md](02-architecture.md) |
| Engenheiro de integração / mantenedor KSC | [03-integration-with-main-tool.md](03-integration-with-main-tool.md) |
| Especialista em segurança | [04-security-and-privacy.md](04-security-and-privacy.md) |
| Revisor de código / QA | [05-testing-and-validation.md](05-testing-and-validation.md) |
| Quem decide sobre colaboração | [07-collaboration-proposal.md](07-collaboration-proposal.md) |

## Índice

| Arquivo | Conteúdo |
|---|---|
| [00-executive-summary.md](00-executive-summary.md) | Resumo executivo (1–2 páginas) |
| [01-technical-overview.md](01-technical-overview.md) | Visão geral, problema, proposta de valor, maturidade |
| [02-architecture.md](02-architecture.md) | Componentes, fluxos, decisões arquiteturais |
| [03-integration-with-main-tool.md](03-integration-with-main-tool.md) | Uso do KSC, interfaces, compatibilidade |
| [04-security-and-privacy.md](04-security-and-privacy.md) | Dados, segredos, superfície de ataque, riscos |
| [05-testing-and-validation.md](05-testing-and-validation.md) | Testes, CI/CD, **validação E2E executada** e evidências |
| [06-known-limitations.md](06-known-limitations.md) | Limitações e riscos para a ferramenta principal |
| [07-collaboration-proposal.md](07-collaboration-proposal.md) | Pedidos específicos à equipe Kaspersky |
| [08-maintainer-questions.md](08-maintainer-questions.md) | Perguntas técnicas objetivas |
| [09-roadmap.md](09-roadmap.md) | Visão do backlog — a fonte da verdade é o [board](https://github.com/orgs/portosoft/projects/1) |
| [10-submission-checklist.md](10-submission-checklist.md) | Checklist de revisão e de submissão |
| [11-outreach-message.md](11-outreach-message.md) | Mensagem de encaminhamento pronta para envio |

## Convenção de evidências

Toda afirmação neste pacote é classificada com um dos rótulos abaixo. Nenhuma
afirmação sem rótulo deve ser tratada como validada.

| Rótulo | Significado |
|---|---|
| `[FATO]` | Verificável no repositório ou em execução reproduzível registrada |
| `[OBSERVADO]` | Resultado obtido em execução, com ambiente e data declarados |
| `[HIPÓTESE]` | Expectativa técnica fundamentada, ainda não medida |
| `[NÃO VALIDADO]` | Implementado, porém sem execução em ambiente real |
| `[LIMITAÇÃO]` | Restrição conhecida e assumida |

## Aviso sobre idioma

Este pacote está em português do Brasil, idioma de todo o repositório.
A tradução para inglês do documento de proposta e do README é item de curto
prazo no [09-roadmap.md](09-roadmap.md) e deve preceder o contato formal com a
equipe internacional da Kaspersky.

## Aviso de independência

Este é um projeto independente, licenciado sob Apache 2.0, sem vínculo,
patrocínio ou endosso da AO Kaspersky Lab. "Kaspersky" e "Kaspersky Security
Center" são marcas de seus respectivos titulares e são citadas aqui apenas para
identificar a ferramenta com a qual o projeto se integra.
