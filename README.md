# KSC Deployment Runbook - Portosoft

Este repositório contém a documentação completa e ferramentas de automação para a implantação do **Kaspersky Security Center (KSC) 16.x** em ambientes Linux (Rocky / Oracle Linux 9) utilizando o banco de dados **PostgreSQL 16**.

## Objetivo
Padronizar e automatizar o processo de instalação do KSC para garantir a repetibilidade, segurança e facilidade de troubleshooting em ambientes internos da Portosoft.

## Escopo
- Instalação e configuração do KSC Administration Server no Linux.
- Preparação e otimização do PostgreSQL 16 para uso com o KSC.
- Configuração de serviços, firewall e conectividade.
- Troubleshooting baseado em incidentes reais e lições aprendidas.
- Automação do setup inicial via Ansible, Bash e Python.

## Fluxo de Implantação
1. **Preparação**: Configuração de Hostname, DNS e atualização do SO.
2. **Banco de Dados**: Instalação e configuração do PostgreSQL 16.
3. **Instalação KSC**: Instalação do servidor e console web via pacotes RPM.
4. **Pós-Instalação**: Validação de serviços, liberação de portas e acesso inicial.
5. **Ajustes Finais**: Configuração de certificados e políticas básicas.

## Estrutura do Repositório
```text
.
├── README.md               # Visão geral e guia rápido
├── .gitignore             # Regras de exclusão do Git
├── LICENSE                # Licença do projeto (Apache-2.0)
├── CONTRIBUTING.md        # Guia de contribuição
├── docs/                  # Documentação técnica detalhada
├── automation/            # Scripts de automação (Ansible, Bash, Python)
├── configs/               # Templates e exemplos de configuração
├── diagrams/              # Diagramas de arquitetura
└── .github/               # Workflows de CI/CD
```

## Segurança
- **NÃO versione segredos**: Jamais comite senhas, arquivos de licença `.key`, certificados privados ou arquivos `.env`.
- Utilize o arquivo `ksc.env.example` como base para suas configurações locais.
- Para automação, prefira o uso de Ansible Vault ou secrets do GitHub Actions.

---
**Mantido pela equipe DevOps Portosoft.**
