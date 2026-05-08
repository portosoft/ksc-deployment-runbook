# Lições Aprendidas

Compilado de insights e boas práticas obtidas através de implantações reais do KSC 16.x em ambientes Linux.

## 1. Planejamento de Hostname
**Lição**: Nunca instale o KSC antes de definir o Hostname final e estável.
- **Por que?**: O KSC utiliza o hostname em vários certificados internos gerados na instalação. Mudar o hostname depois exige a reinstalação ou procedimentos complexos de troca de certificados.

## 2. PostgreSQL Minimalista
**Lição**: Em instalações "Minimal" do Linux, o PostgreSQL pode não trazer todas as dependências de libs que o KSC espera.
- **Ação**: Sempre instale o grupo de pacotes "Development Tools" ou garanta que `perl` e `zlib` estejam presentes.

## 3. Ordem de Instalação do DB
**Lição**: O banco de dados deve estar 100% funcional e com as strings de conformidade ajustadas **antes** de chamar o `postinstall.pl`.
- **Ação**: Validar com `psql` a conectividade local antes de prosseguir.

## 4. Atenção ao Firewall
**Lição**: O Rocky Linux 9 utiliza o `nftables` via `firewalld`. Regras manuais de `iptables` podem ser ignoradas ou sobrescritas.
- **Ação**: Utilize sempre o `firewall-cmd` para persistência das regras.

## 5. Web Console e IAM
**Lição**: A Web Console e o IAM são serviços distintos. Se a console carrega mas o login falha sem erro de "senha incorreta", o problema geralmente está no serviço IAM ou na comunicação dele com o banco de dados.

## 6. Backup é Vida
**Lição**: O backup nativo do KSC (`klbackup`) é essencial, mas ter um snapshot da VM ou um backup do volume do PostgreSQL salva horas de retrabalho em caso de falha no upgrade de versão.
