import paramiko

import os

host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)

    result_text = """### RESULTADO DA INTERVENCAO KSC 16.x ###
1. Tentativa de Recuperacao (Passo 1):
   - iam_config.yaml limpo foi injetado com permissoes corretas.
   - O servico kliam_srv leu as configuracoes mas falhou (FATAL: banco de dados ksciam nao existe).
   - Resultado: Recuperacao impossivel, o banco relacional de identidades foi deletado/corrompido.

2. Limpeza e Replantacao (Passo 3 e 4):
   - Evidencias preservadas em /root/ksc_recovery_evidence/{logs,configs}.
   - Remocao do ksc64 via yum remove apresentou "Error in PREUN scriptlet in rpm package ksc64" devido ao estado incosistente.
   - Os diretorios /var/opt/kaspersky e /etc/opt/kaspersky foram movidos para *.broken-YYYYMMDD para evitar heranca maldita.
   - A reinstalacao sofreu bloqueio pela transacao corrompida do RPM que impediu a gravacao nativa via yum.

ESTADO FINAL: Servidor encontra-se com as evidencias presasvetadas. O pacote RPM 'ksc64' esta em estado 'broken/half-installed'.
Acao requerida pelo operador: Executar 'rpm -e --noscripts ksc64' para limpar o ghost RPM e re-executar a instalacao.
"""

    stdin, stdout, stderr = client.exec_command(
        f"echo '{password}' | sudo -S sh -c \"cat > /root/ksc_recovery_evidence/RESULTADO.txt << 'EOF'\n{result_text}\nEOF\""
    )
    print(stdout.read().decode("utf-8"))
    print(stderr.read().decode("utf-8"))

except Exception as e:
    print(e)
finally:
    client.close()
