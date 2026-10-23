# Evidências do rollback verificado — issue #223

Execuções reais na VM Rocky Linux 9.8 do laboratório Proxmox, em 2026-09-13,
sobre a instalação de KSC 16.3.0.1207 validada em #209.

| Arquivo | Conteúdo | Resultado |
|---|---|---|
| `01-rollback-instalacao-parcial.log` | `rollback --check` e `rollback --apply --verify` sobre instalação interrompida | exit 0, **zero resíduos** |
| `02-reinstalacao-apos-rollback.log` | `setup --apply` e `audit --postcheck` logo após o rollback | exit 0, zero críticos, Web Console HTTP 200 |

## Cenário exercitado

A VM foi restaurada ao snapshot `packages-ready` e o `setup --apply` foi
iniciado e **morto durante a execução do `postinstall.pl`**, produzindo uma
instalação parcial real: três RPMs instalados, bases `ksc` e `ksciam` criadas,
contas `ksc` e `kladmins` presentes, diretórios do produto no disco, porém
**nenhuma unidade systemd** — o instalador não chegou a criá-las.

É o estado mais difícil de recuperar, e o que a issue pedia.

## Resultado

O `kscctl rollback --apply --verify` deixou o host sem nenhum resíduo,
confirmado por inspeção independente: zero pacotes, zero bases, zero roles,
contas ausentes, diretórios ausentes, drop-ins ausentes, zero unidades.

A reinstalação subsequente concluiu com sucesso, o pós-check não acusou falhas
críticas e o Web Console respondeu HTTP 200 em `/login`. **Não foi necessário
reiniciar o host**, ao contrário do que a documentação anterior afirmava.

## O que o procedimento anterior deixava para trás

Antes de escrever o novo comando, o procedimento de `docs/11-rollback.md` foi
executado literalmente sobre uma instalação completa. Restaram sete resíduos:

| Resíduo | Causa |
|---|---|
| RPM `klnagent64` | O procedimento removia apenas `ksc64` e `ksc-web-console` |
| Base `ksciam` | O procedimento citava apenas `ksc` |
| Role `kluser` | O procedimento removia `ksc_admin`, que o runbook nunca cria |
| Conta de sistema `ksc` | Não mencionada |
| Grupo `kladmins` | Não mencionado |
| `/etc/ksc-web-console-setup.json` e `/var/log/kaspersky` | Não mencionados |
| Drop-ins systemd | Sobreviviam às unidades que estendiam |

Observação relevante: mesmo com esses resíduos, a reinstalação funcionou —
mas **reaproveitando a base `ksciam` anterior**, de modo que o servidor novo
herdava o estado de identidade do anterior. Um rollback que preserva a base do
IAM não devolve o host ao estado limpo, ainda que a instalação seguinte pareça
bem-sucedida.

## Decisão sobre automação

O procedimento **pode** ser automatizado com segurança e passou a ser, como
`kscctl rollback`. As salvaguardas adotadas:

- `--apply` exige `--confirm-token ROLLBACK-CONFIRM`, como as demais operações
  destrutivas da CLI;
- `--check` lista o que seria removido sem tocar no sistema;
- `--verify` percorre o host ao final e falha se houver resíduo;
- banco de dados remoto nunca é tocado.

## Limitação

Exercitado em **um** cenário de instalação parcial (interrupção durante o
`postinstall.pl`) e em **uma** instalação completa. Outros pontos de
interrupção — durante o `dnf install`, durante a configuração do Web Console —
não foram testados.
