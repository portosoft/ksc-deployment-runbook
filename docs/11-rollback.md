# 11 - Rollback

## Objetivo
Devolver o host ao estado anterior ao deploy quando a instalação falhar de
forma irrecuperável, de modo que uma reinstalação limpa seja possível.

> [!WARNING]
> O rollback é **destrutivo e irreversível**. Ele remove os pacotes do KSC, as
> bases `ksc` e `ksciam`, a role de aplicação, as contas de sistema e os
> diretórios do produto. Não há backup automático: se houver dado a preservar,
> faça a cópia antes.

## Procedimento

```bash
# 1. Ver o que seria removido, sem alterar nada
python3.11 -m automation.python.kscctl rollback --check

# 2. Executar, verificando ao final se sobrou algum resíduo
sudo python3.11 -m automation.python.kscctl rollback \
  --apply --confirm-token ROLLBACK-CONFIRM --verify
```

O comando termina com código diferente de zero se a verificação encontrar
resíduos, e lista cada um deles.

## O que é removido

| Item | Detalhe |
| :--- | :--- |
| Serviços | Unidades do Administration Server, Network Agent, IAM e Web Console, paradas e desabilitadas antes de qualquer remoção |
| Pacotes | `ksc64`, `klnagent64` e `ksc-web-console` |
| Bases de dados | `ksc` e `ksciam`, com as conexões encerradas antes do `DROP` |
| Role | A role configurada em `KSC_DB_USER` |
| Contas de sistema | Usuário `ksc` e grupo `kladmins` |
| Diretórios | `/opt/kaspersky`, `/var/opt/kaspersky`, `/var/log/kaspersky`, `/var/lib/ksc-web-console` |
| Configuração | `/etc/ksc-web-console-setup.json` |
| Drop-ins systemd | Os criados pelo runbook para `LD_LIBRARY_PATH` e para a capacidade de porta privilegiada |

**Banco de dados remoto é preservado.** Se `KSC_DB_HOST` apontar para outro
servidor, as bases e a role não são tocadas: removê-las é decisão do
administrador daquele banco.

## Ordem das operações

A sequência não é arbitrária, e alterá-la quebra o procedimento:

1. **Serviços primeiro** — evita processos escrevendo em diretórios que estão
   sendo apagados e conexões abertas contra as bases.
2. **Conexões encerradas antes do `DROP DATABASE`** — uma sessão remanescente
   faz o comando falhar com *"database is being accessed by other users"*.
3. **Contas de sistema por último** — removê-las antes deixaria sem dono
   conhecido os arquivos que ainda precisam ser apagados.

Cada passo tolera ausência, de modo que o mesmo comando serve tanto a uma
instalação completa quanto a uma interrompida pela metade.

## Reinstalação

Após o rollback, a reinstalação é a sequência normal:

```bash
python3.11 -m automation.python.kscctl audit --check
sudo python3.11 -m automation.python.kscctl setup --apply
```

Reiniciar o host não é necessário. Verificado em 2026-09-13: rollback sobre
uma instalação interrompida no meio do `postinstall.pl`, seguido de
reinstalação completa com pós-check sem falhas críticas e Web Console
acessível. Evidências em `evidence/e2e-223/`.

## Procedimento manual

Se por algum motivo o `kscctl` não estiver disponível, os passos equivalentes
são os abaixo. Note que a versão anterior desta página estava incompleta:
esquecia o `klnagent64`, a base `ksciam`, as contas de sistema e os drop-ins, e
tentava remover uma role `ksc_admin` que o runbook nunca cria.

```bash
# Serviços
sudo systemctl disable --now kladminserver_srv klnagent_srv kliam_srv klwebsrv_srv \
  KSCWebConsole KSCSvcWebConsole KSCWebConsoleManagement KSCWebConsoleNATS KSCWebConsolePlugin

# Pacotes
sudo dnf remove -y ksc64 klnagent64 ksc-web-console

# Bases e role (ajuste o nome da role ao seu KSC_DB_USER)
sudo -u postgres psql <<'SQL'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
 WHERE datname IN ('ksc', 'ksciam') AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS "ksc";
DROP DATABASE IF EXISTS "ksciam";
DROP ROLE IF EXISTS "kluser";
SQL

# Diretórios, configuração e drop-ins
sudo rm -rf /opt/kaspersky /var/opt/kaspersky /var/log/kaspersky /var/lib/ksc-web-console
sudo rm -f /etc/ksc-web-console-setup.json
sudo rm -rf /etc/systemd/system/kladminserver_srv.service.d \
            /etc/systemd/system/KSCWebConsole.service.d
sudo systemctl daemon-reload

# Contas de sistema, por último
sudo userdel ksc
sudo groupdel kladmins
```

---
[Próximo Passo: FAQ >>](12-faq.md)
