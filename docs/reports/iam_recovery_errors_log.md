# Log de Recuperação e Erros: Incidente KSC IAM 16.x

**Data:** Maio de 2026
**Incidente:** O serviço `kliam_srv` entrou em loop de reinicialização (`status=1/FAILURE`) devido à ausência do arquivo de configuração `/var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml`.

Este documento registra todas as tentativas, erros enfrentados e as contramedidas adotadas durante o processo de *troubleshooting* e reinstalação.

---

## 1. Tentativa de Recuperação Mínima (Injeção de YAML)

**O que foi tentado:**
Como o arquivo `iam_config.yaml` havia sumido, tentamos injetar um modelo limpo gerado anteriormente, ajustando permissões (`chown ksc:kladmins` e `chmod 640`).
**Erro Enfrentado:**
```text
failed to migrate: migration error, type: 1: failed to open database: failed to connect to `host=127.0.0.1 user=kluser database=ksciam`: server error (FATAL: não existe o banco de dados "ksciam" (SQLSTATE 3D000))
```
**Causa:** Durante um script de rollback efetuado anteriormente, o banco `ksciam` falhou ao ser criado. A falta da base relacional inviabilizou a recuperação simples do serviço IAM. A ação tomada foi declarar o estado como irrecuperável e prosseguir para a reinstalação.

---

## 2. Falha na Recriação da Base (Locale Mismatch)

**O que foi tentado:**
Criar a base de dados do IAM manualmente via PSQL no script de rollback.
**Erro Enfrentado:**
```text
ERRO: nova ordenação (en_US.UTF-8) é incompatível com a ordenação do banco de dados modelo (pt_BR.UTF-8)
DICA: Use a mesma ordenação do banco de dados modelo ou use template0 como modelo.
```
**Causa/Solução:** O script tentou forçar o Collate `en_US.UTF-8`, porém o template do SO/Postgres remoto estava em `pt_BR.UTF-8`.
A solução adotada nas tentativas seguintes foi criar explicitamente os bancos com `LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8'`.

---

## 3. Falha na Desinstalação do Pacote RPM (PREUN scriptlet)

**O que foi tentado:**
Limpeza do ambiente usando `yum remove -y ksc64 ksc64-web-console klnagent64`.
**Erro Enfrentado:**
```text
Error in PREUN scriptlet in rpm package ksc64
Erro: Transação falhou
```
**Causa/Solução:** Os diretórios base e serviços estavam num estado tão quebrado que os scripts internos de pré-desinstalação do RPM travaram o gerenciador de pacotes, deixando o KSC como um pacote fantasma (*half-installed*).
A solução foi forçar a remoção ignorando a trava de segurança via `rpm -e --noscripts ksc64 klnagent64 ksc-web-console`.

---

## 4. Falha na Subida do IAM por Porta Ocupada (Ghost Process)

**O que foi tentado:**
Após recriar o banco `ksciam` limpo, tentou-se reiniciar o `kliam_srv`.
**Erro Enfrentado:**
```text
failed to start TLS listener ... error: listen tcp 127.0.0.1:13299: bind: address already in use
```
**Causa/Solução:** Um processo zumbi do IAM continuava ocupando a porta 13299.
A solução foi acionar o utilitário `fuser 13299/tcp` para localizar o PID e usar `kill -9` para liberar a porta antes do restart do systemd.

---

## 5. Falha Final na Assinatura (JWE Certs Mismatch)

**O que foi tentado:**
Com o banco RPM limpo, os pacotes reinstalados (`yum install ksc64-16.2.0-1023.x86_64.rpm`), e o `postinstall.pl` concluído, o Administration Server (`klserver`) subiu corretamente. Tentamos reinjetar o `iam_config.yaml`.
**Erro Enfrentado:**
O serviço `kliam_srv` continua falhando e saindo com status 1.
**Causa/Solução Pendente:** A limpeza extremada apagou a pasta `/var/opt/kaspersky`. Isso significa que os certificados locais do servidor (como `/var/opt/kaspersky/klnagent_srv/1093/cert/klsrvJWEsign.cer`) foram destruídos e novos foram gerados pelo KSC Server durante a reinstalação. Como o nosso YAML injetado refere-se aos *hashes* ou nomes das chaves antigas perdidas, o Identity Manager falha ao decriptar os tokens e aborta.
**Ação Final Requerida:** Executar o utilitário do KSC (ex: utilitário OpenAPI ou de regeneração IAM) para regerar os certificados de integração do IAM e povoar um novo YAML, em vez de depender do YAML estático.

---
*Fim do Relatório*
