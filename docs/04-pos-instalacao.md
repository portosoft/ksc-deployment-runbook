# 04 - Pós-instalação e Validação

Após a instalação bem-sucedida, valide o ambiente.

## Serviços e Portas
- Verifique se todos os serviços estão `active (running)`:
  `kladminserver_srv`, `KSCWebConsole.service`.
- Verifique se as portas estão em escuta:
  `8080`, `13000`, `13299`, `5432`.

## Usuário Admin
Crie o usuário administrador da interface web:
```bash
sudo /opt/kaspersky/ksc64/sbin/kladduser -n KLAdmins -u ksc_admin -p <SENHA> -r Administrator
```

## Firewall
Garanta que as portas necessárias estejam abertas:
```bash
sudo firewall-cmd --permanent --add-port={8080,13000,13299}/tcp
sudo firewall-cmd --reload
```
