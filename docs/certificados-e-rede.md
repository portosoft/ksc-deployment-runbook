# Certificados e Rede

A segurança da comunicação no Kaspersky Security Center depende de uma configuração de rede sólida e do uso correto de certificados.

## Comunicação de Rede

### Uso de FQDN (Fully Qualified Domain Name)
É altamente recomendado que o servidor KSC seja configurado e acessado via FQDN (ex.: `ksc.portosoft.com.br`) em vez de apenas o endereço IP.
- **Vantagem**: Facilita a substituição do servidor e a renovação de certificados.
- **Configuração**: Garanta que o DNS interno resolva o nome corretamente para todos os end-points.

### Acesso Externo e VPN
Para gerenciar dispositivos fora da rede corporativa:
- Utilize o **Gateway de Conexão** (Connection Gateway) da Kaspersky.
- Ou utilize soluções de VPN (como Tailscale ou OpenVPN) para manter o tráfego dentro de um túnel seguro.
- A porta 13000/tcp deve estar acessível para os agentes reportarem.

## Gestão de Certificados

### Certificados da Web Console
Por padrão, a Web Console gera um certificado auto-assinado.
- **Produção**: Recomenda-se substituir pelo certificado emitido pela CA da empresa ou um certificado público (ex.: Let's Encrypt).
- **Caminho padrão**: Os certificados costumam ficar em `/var/opt/kaspersky/ksc64/certificates/`.

### Boas Práticas de Segurança
- **Não exponha chaves privadas**: Jamais envie arquivos `.key` para repositórios de código.
- **Backup de Certificados**: O backup do KSC inclui os certificados do servidor. Sem eles, os agentes perdem a comunicação com o servidor em caso de restore.
- **Criptografia**: Toda a comunicação entre Agente e Servidor utiliza SSL/TLS por padrão na porta 13000.

## Tabela de Referência de Rede

| Componente | Porta | Protocolo | Necessário |
| :--- | :--- | :--- | :--- |
| Web Console HTTPS | 8443 | TCP | Sim |
| Agente para Server | 13000 | TCP | Sim |
| Server para Agente | 15000 | UDP | Não (Otimização) |
| Web Console HTTP | 8080 | TCP | Opcional (Redirect) |
