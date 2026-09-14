# Evidências da idempotência verificada — issue #228

Execuções reais na VM Rocky Linux 9.8 do laboratório, em 2026-09-13, sobre a
instalação de KSC 16.3.0.1207 validada em #209.

| Arquivo | Conteúdo |
|---|---|
| `01-segunda-execucao.log` | Reexecução de `setup --apply` em host já instalado |
| `02-diff-estado.log` | Diff da impressão de estado entre três execuções consecutivas |
| `03-postcheck-final.log` | Pós-check e certificado após as reexecuções |
| `04-fingerprint.txt` | Impressão completa do estado do host |

## Método

Comparar apenas o relatório de auditoria seria insuficiente — e isto não é uma
suposição: no primeiro ciclo o relatório saiu **idêntico** enquanto o
certificado TLS do Web Console havia sido substituído.

Por isso a verificação usa `automation/bash/state-fingerprint.sh`, que produz
uma saída ordenada e estável cobrindo pacotes, unidades systemd com estado de
habilitação, portas em escuta, contas de sistema, bases e roles, permissões e
donos dos diretórios do produto, hashes dos arquivos de configuração e o
fingerprint do certificado do Web Console.

## Dois defeitos encontrados

### 1. A segunda execução simplesmente abortava

```
[CRITICAL] port_13000: Porta 13000 em uso.
[CRITICAL] port_443: Porta 443 em uso.
Falha na instalação: Prechecks falharam criticamente.
```

São as portas que o próprio KSC passou a ocupar. O pré-check avalia condições
de partida, e num host já instalado "porta em uso" é o estado correto. A
verificação de portas passou a ser omitida quando há um Administration Server
configurado; as demais continuam valendo.

### 2. O certificado TLS era trocado silenciosamente

Com o defeito anterior corrigido, a segunda execução concluía — mas o diff de
estado mostrou:

```
< /var/opt/kaspersky/ksc-web-console/KLRootCA.crt 62:04:00:1B:DE:3E:AD:35:...
> /var/opt/kaspersky/ksc-web-console/KLRootCA.crt 93:63:5C:FD:46:A8:E2:B5:...
```

e as contas de serviço do componente recriadas com novos nomes aleatórios
(`user_management_eog-mcpkzf` → `user_management_3r5ggq_yg8`).

A causa é o `setup.js` do Web Console, que regenera certificados e contas a
cada invocação. O efeito prático: qualquer cliente que já tivesse aceitado o
certificado anterior passaria a falhar, **sem que o relatório de auditoria
acusasse mudança alguma** — o diff daquele relatório foi vazio.

A configuração do Web Console passou a ser ignorada quando a unidade já existe
e os parâmetros em `/etc` são idênticos aos desejados. Parâmetros diferentes
continuam disparando o `setup.js`, porque aí a reconfiguração é intencional.

## Resultado

Com as duas correções, **três execuções consecutivas de `setup --apply`
deixaram a impressão de estado byte a byte idêntica**:

```
### diff execução 1 -> 2
(idêntico)
### diff execução 2 -> 3
(idêntico)
```

O servidor seguiu saudável ao final: pós-check sem falhas críticas, Web Console
respondendo HTTP 200 em `/login` e o certificado com o mesmo fingerprint de
antes das reexecuções.

## Limitações

- Verificado em **um** host, com os mesmos parâmetros de configuração em todas
  as execuções. Reexecutar com parâmetros alterados dispara reconfiguração
  deliberada e não foi exercitado.
- A impressão de estado não cobre o conteúdo das bases de dados: mudanças
  internas ao KSC entre execuções não seriam detectadas por ela.
