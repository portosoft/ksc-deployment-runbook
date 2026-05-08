import os
import sys
import paramiko
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env local
load_dotenv(os.path.join(os.path.dirname(__file__), '../../configs/.env'))

def run_ssh_commands(host, user, password, commands):
    """Executa comandos via SSH com ***REMOVED*** a sudo"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    results = []
    try:
        client.connect(host, username=user, password=password, timeout=15)
        for cmd in commands:
            # Comando com sudo -S para ler senha do stdin
            full_cmd = f"sudo -S {cmd}"
            stdin, stdout, stderr = client.exec_command(full_cmd)
            stdin.write(password + '\n')
            stdin.flush()
            
            res = {
                'command': cmd,
                'stdout': stdout.read().decode('utf-8'),
                'stderr': stderr.read().decode('utf-8'),
                'status': stdout.channel.recv_exit_status()
            }
            results.append(res)
        client.close()
    except Exception as e:
        print(f"Erro de Conexão SSH: {e}")
        return None
    return results

def main():
    host = os.getenv('KSC_HOST')
    user = os.getenv('KSC_USER')
    password = os.getenv('KSC_PASS')

    if not all([host, user, password]):
        print("Erro: Variáveis de ambiente (KSC_HOST, KSC_USER, KSC_PASS) não encontradas.")
        print("Certifique-se de que o arquivo configs/.env existe.")
        sys.exit(1)

    print(f"--- Iniciando Auditoria Operacional em {host} ---")

    audit_cmds = [
        "hostnamectl | grep 'Operating System'",
        "systemctl is-active postgresql.service",
        "netstat -tlnp | grep -E '13000|13001|8443|8080'",
        "firewall-cmd --list-all",
        "sudo -u postgres psql -c '\\du' | grep kluser",
        "ls -la /opt/kaspersky/ksc64/sbin/klserver || echo 'KSC Server não instalado'",
        "df -h /tmp"
    ]

    results = run_ssh_commands(host, user, password, audit_cmds)
    
    if results:
        for r in results:
            print(f"\n[+] Comando: {r['command']}")
            if r['status'] == 0:
                print(r['stdout'].strip())
            else:
                print(f"AVISO: Comando retornou status {r['status']}")
                if r['stderr']: print(f"ERRO: {r['stderr'].strip()}")
    
    print("\n--- Auditoria Finalizada ---")

if __name__ == "__main__":
    main()
