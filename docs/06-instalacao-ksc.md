# 06 - Instalação KSC

## Objetivo
Realizar a instalação silenciosa do KSC Administration Server e Web Console.

## Entradas Necessárias
- Arquivo de variáveis: `configs/env/.ksc_vars.env`.
- Arquivo de respostas: `configs/ksc/ksc_response.txt.template`.

## Procedimento
1. **Baixar Pacotes**: Obtenha os arquivos `.rpm` oficiais do site da Kaspersky.
2. **Executar Instalação**:
```bash
python3 automation/python/ksc_setup.py --apply
```

## Pontos de Atenção (Incidentes Reais)
- Se o script falhar com erro de banco, verifique se a senha no `.env` possui caracteres especiais que não foram escapados.
- Se o Web Console não subir, certifique-se que o NodeJS compatível está instalado.

## Gate de Passagem
O comando `systemctl status klserver` deve reportar `active`.

---
[Próximo Passo: Pós-instalação e Validação >>](07-pos-instalacao-validacao.md)
