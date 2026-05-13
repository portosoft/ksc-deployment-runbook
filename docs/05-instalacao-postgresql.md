# 05 - Instalação PostgreSQL

## Objetivo
Instalar o PostgreSQL 16 e prepará-lo para a carga de trabalho do KSC.

## Comandos de Instalação (Local)
```bash
# Instalar repositório e pacotes
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo dnf -qy module disable postgresql
sudo dnf install -y postgresql16-server

# Inicializar o banco
sudo /usr/pgsql-16/bin/postgresql-16-setup initdb

# Ativar e iniciar
sudo systemctl enable --now postgresql-16
```

## Otimização (Hardening/Tuning)
Execute o script de hardening do banco para ajustar `max_connections` e autenticação:

```bash
python3 automation/python/ksc_harden_db.py --apply
```

## Validação
- Verifique se o serviço está `active (running)`.
- Verifique se a porta `5432` está aberta localmente.

---
[Próximo Passo: Instalação KSC >>](06-instalacao-ksc.md)
