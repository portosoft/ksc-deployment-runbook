# 7. Proposta de colaboração

## 7.1 O que estamos pedindo

Cinco solicitações objetivas e respondíveis. Nenhuma delas exige compromisso de
suporte, endosso ou trabalho de engenharia significativo por parte da equipe
Kaspersky.

| # | Solicitação | Motivo | Benefício para a Kaspersky | Esforço esperado | Dependência | Prioridade |
|---|---|---|---|---|---|---|
| S-01 | Classificar as interfaces listadas em [03 §3.2](03-integration-with-main-tool.md) como estáveis, instáveis ou impróprias para uso por terceiros | Hoje dependemos de comportamento observado em três pontos críticos | Evita que integrações de terceiros dependam de superfícies internas e gerem chamados de suporte | Baixo — revisão de uma tabela | Nenhuma | Alta |
| S-02 | Indicar o método suportado para configurar o Web Console, se existir alternativa a editar `config.json` | Remover nossa dependência mais frágil (L-04) | Reduz o número de instalações de terceiros mexendo em arquivos internos | Baixo | S-01 | Alta |
| S-03 | Confirmar o formato e as chaves obrigatórias do arquivo de respostas da instalação silenciosa | Nossa reprodutibilidade entre servidores depende disso (AD-4) | Instalações silenciosas corretas em campo | Baixo a médio | Nenhuma | Alta |
| S-04 | Revisão de segurança do nosso modelo de privilégio e do manuseio de segredos, especialmente o conjunto mínimo de `sudo` por operação | Não temos hoje um princípio de menor privilégio definido (§4.3) | Reduz o risco de hosts de administração sobreprivilegiados no ecossistema | Médio | [04](04-security-and-privacy.md) | Média |
| S-05 | Orientação sobre marca, nomenclatura e forma de referência ao produto aceitável para um projeto independente | Queremos estar em conformidade antes de qualquer divulgação | Protege a marca; evita percepção de endosso | Baixo | Nenhuma | Média |

## 7.2 O que **não** estamos pedindo neste momento

- Não pedimos inclusão em ecossistema oficial, listagem em marketplace ou
  qualquer forma de endosso.
- Não pedimos alteração no produto, nova API ou aceitação de pull request.
- Não pedimos suporte a usuários do nosso projeto.

Esses assuntos só fariam sentido após a validação end-to-end descrita em
[09-roadmap.md](09-roadmap.md), e só serão propostos se houver interesse
manifesto da equipe.

## 7.3 O que oferecemos em contrapartida

| Oferta | Estado |
|---|---|
| Casos de falha reproduzíveis de instalação em Rocky/Oracle Linux 9, com logs estruturados | Parcial — depende do ciclo E2E (R-01) |
| Relatórios de defeito qualificados, com evidência e ambiente declarados | Disponível a partir de R-01 |
| Ambiente de laboratório reproduzível (Proxmox em Podman rootless) para reprodução de cenários | Definido, execução pendente |
| Material de referência operacional em português sobre KSC em Linux | Disponível hoje |
| Ajuste ou remoção imediata de qualquer uso que a equipe considere impróprio | Compromisso assumido |

## 7.4 Como avaliar o projeto

| Objetivo do revisor | Caminho mais curto |
|---|---|
| Entender o escopo em 10 minutos | [00-executive-summary.md](00-executive-summary.md) |
| Avaliar a integração | [03-integration-with-main-tool.md](03-integration-with-main-tool.md) §3.2 e §3.3 |
| Avaliar o código | `automation/python/` (núcleo) e `automation/ops/` (operações); `kscctl.py` é o ponto de entrada |
| Rodar a suíte de testes | `python3 -m pytest -q` na raiz do repositório |
| Ver o contrato da CLI | `python3 -m automation.python.kscctl --help` |
| Conferir o gate de integridade | `configs/ksc/packages.json`, `configs/ksc/checksums.sha256`, `automation/python/packages.py` |
| Avaliar segurança | [04-security-and-privacy.md](04-security-and-privacy.md) e os workflows em `.github/workflows/` |

Todo o material é público sob Apache 2.0. Não há NDA envolvido e não há
componente proprietário no projeto.

## 7.5 Próximos passos propostos

1. Envio deste pacote e da mensagem em [11-outreach-message.md](11-outreach-message.md).
2. Resposta às perguntas Q1–Q7 de [08-maintainer-questions.md](08-maintainer-questions.md), por escrito ou em uma sessão técnica de 45 minutos.
3. Em paralelo e independentemente da resposta: execução de R-01 a R-04 do backlog canônico.
4. Reapresentação do pacote com as evidências de R-01 incorporadas, momento em que a prontidão poderá ser reclassificada para "pronto para piloto".
