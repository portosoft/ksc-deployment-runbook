# Proxmox VE em Container — Laboratório de Testes KSC

Infraestrutura containerizada para execução e validação ponta a ponta (E2E) do Kaspersky Security Center 16.x em Rocky Linux 9 / Oracle Linux 9, utilizando o projeto [dockur/proxmox](https://github.com/dockur/proxmox).

---

## 🏗️ Visão Geral

Este ambiente sobe um nó Proxmox VE 9.x isolado via **Podman rootless** e sidecars `socat` para encaminhamento transparente de portas de rede para a VM de testes (IP interno sugerido: `172.30.5.10`).

### Mapa de Portas Encaminhadas

| Porta no Host (127.0.0.1) | Porta na VM (172.30.5.10) | Serviço / Finalidade |
| :--- | :--- | :--- |
| `8006` | — | Interface Web do Proxmox VE (`https://127.0.0.1:8006/`) |
| `2222` | `22` | SSH para a VM de teste |
| `8443` | `443` | Web Console HTTPS do KSC |
| `8080` | `8080` | Web Console HTTP / Alternativa |
| `13291` | `13291` | KSC Administration Server (Console API) |
| `13000` | `13000` | Kaspersky Network Agent (SSL) |
| `14000` | `14000` | Kaspersky Network Agent (Plain/SSL) |
| `5432` | `5432` | PostgreSQL 16 |

---

## 🚀 Como Subir o Ambiente

### 1. Criar o arquivo de segredos do Proxmox (fora do Git)

```bash
mkdir -p ~/.secrets
install -m 600 /dev/null ~/.secrets/ksc-proxmox.env
printf 'PROXMOX_PASSWORD=%s\n' "$(openssl rand -base64 24 | tr -d '/+=')" > ~/.secrets/ksc-proxmox.env
```

### 2. Inicializar os Containers

```bash
podman compose --env-file ~/.secrets/ksc-proxmox.env \
  -f infra/proxmox/compose.yml up -d
```

### 3. Verificar o Status

```bash
podman ps --filter name=ksc-proxmox
curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1:8006/
# Código HTTP esperado: 200
```

Para detalhes completos de provisionamento da VM Rocky Linux 9, configuração de IP e ciclo de testes, consulte o documento oficial:
👉 [docs/14-ambiente-testes-proxmox.md](../../docs/14-ambiente-testes-proxmox.md)
