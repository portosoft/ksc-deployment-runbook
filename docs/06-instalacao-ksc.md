# 06 - Instalação KSC

## Objetivo
Realizar a instalação silenciosa do KSC Administration Server e Web Console.

## Entradas Necessárias
- Arquivo de variáveis: `configs/env/.ksc_vars.env`.
- Template de respostas: `configs/ksc/ksc_response.txt.template`.

> O arquivo de respostas final é gerado dinamicamente pela automação de reconfiguração a partir desses parâmetros, sem exigir commit de uma versão preenchida.

## Procedimento

### 1. Obtenção e Verificação Criptográfica de Pacotes

Todos os binários oficiais devem ser obtidos do portal da Kaspersky:
- **Portal Oficial**: [Kaspersky Endpoint Security Downloads](https://www.kaspersky.com/small-to-medium-business-security/downloads/endpoint)
- **Catálogo Automatizado do Projeto**: `configs/ksc/packages.json`
- **Arquivo de Hashes**: `configs/ksc/checksums.sha256`

> [!IMPORTANT]
> **Defesa em Profundidade / Zero Trust**: Nunca instale pacotes RPM sem antes validar a integridade criptográfica contra os hashes SHA-256 oficiais publicados pelo fabricante.

#### Tabela de Pacotes e Hashes Oficiais (KSC 16.3 & KESL 12.5)

| Componente | Idioma | Arquivo RPM / Pacote | Hash SHA-256 Oficial |
| :--- | :--- | :--- | :--- |
| **KSC Server 16.3** | pt-BR | `ksc64-16.3.0-1207.x86_64.rpm` | `32401411366de1ceb7fdfe79a233c49031d31a8f0e11270e14e8c21ded545abb` |
| **KSC Server 16.3** | en-INT | `ksc64-16.3.0-1207.x86_64.rpm` | `dab517df732a0e12bc34c379b101b8e02e9c33e320443e6494817e0872889a75` |
| **KSC Web Console 16.3** | pt-BR | `ksc-web-console-16.3.12907.x86_64.rpm` | `a55b91fb45a523daf7b5b477671ab84624d184a8e295946e3698c19b27e747d2` |
| **KSC Web Console 16.3** | en-INT | `ksc-web-console-16.3.12907.x86_64.rpm` | `a55b91fb45a523daf7b5b477671ab84624d184a8e295946e3698c19b27e747d2` |
| **Network Agent 16.3** | pt-BR | `klnagent64-16.3.0-1207.x86_64.rpm` | `eef05713088fa9db44ca91ebe77ace0d5e9999f4ff1ef15601fb60d68d00d28f` |
| **Network Agent 16.3** | en-INT | `klnagent64-16.3.0-1207.x86_64.rpm` | `dc71fe6bf6c69079ca5c7b1f2403ee2a6fbd1dffb2cf2ee6010d94b1469e7f58` |
| **KESL 12.5 (Distributive)** | Multi | `kesl-12.5.0-1569.x86_64.rpm` | `c29bb66d11e36401ab095449cf441fd8551e41267424f4d44a51e9fe45f01d41` |
| **KESL 12.5 (GUI)** | Multi | `kesl-gui-12.5.0-1569.x86_64.rpm` | `164e5bff0c8006c12bd445416da21425d98e7f0c0e67912164ac8420a61306c9` |

#### Opção A — Download Automatizado com Verificação

Para listar os pacotes disponíveis:
```bash
python3 -m automation.python.kscctl packages --list
```

Para baixar um pacote diretamente com verificação automática:
```bash
python3 -m automation.python.kscctl packages --download ksc-server-16.3-pt-BR --output-dir /var/tmp/ksc_packages
```

#### Opção B — Verificação de Pacotes Já Baixados

Se os pacotes foram transferidos manualmente para um diretório (ex: `/var/tmp/ksc_packages`):

```bash
# Via CLI do runbook:
python3 -m automation.python.kscctl packages --verify-dir /var/tmp/ksc_packages

# Ou via comando nativo do Linux:
cd /var/tmp/ksc_packages
sha256sum -c /caminho/para/ksc-deployment-runbook/configs/ksc/checksums.sha256 --ignore-missing
```

### 2. Executar Instalação
```bash
python3 -m automation.python.ksc_setup --apply
```

## Pontos de Atenção (Incidentes Reais)
- Se o script falhar com erro de banco, verifique se a senha no `.env` possui caracteres especiais que não foram escapados.
- Se o Web Console não subir, certifique-se que o NodeJS compatível está instalado.

## Gate de Passagem
O comando `systemctl status klserver` deve reportar `active`.

---
[Próximo Passo: Pós-instalação e Validação >>](07-pos-instalacao-validacao.md)
