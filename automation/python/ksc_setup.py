import os
import sys
import paramiko
from dotenv import load_dotenv

# Carrega variáveis de um arquivo .env se existir
load_dotenv()

def run_ssh_commands_with_sudo(host, user, password, commands):
    """Executa comandos via SSH com ***REMOVED*** a sudo e senha."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        results = []
        for cmd in commands:
            full_cmd = f"sudo -S {cmd}"
            stdin, stdout, stderr = client.exec_command(full_cmd)
            stdin.write(password + '\n')
            stdin.flush()
            
            # Captura saída
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            exit_status = stdout.channel.recv_exit_status()
            
            results.append({
                'command': cmd,
                'stdout': out,
                'stderr': err,
                'exit_status': exit_status
            })
        client.close()
        return results
    except Exception as e:
        print(f"Erro na conexão SSH: {str(e)}")
        return None

def main():
    # Recupera configurações das variáveis de ambiente
    host = os.getenv('KSC_HOST', '***REMOVED***')
    user = os.getenv('KSC_USER', '***REMOVED***')
    password = os.getenv('KSC_PASS')
    db_pass = os.getenv('KSC_DB_PASS', 'REDACTED_DB_PASS')
    
    if not password:
        print("ERRO: Variável de ambiente KSC_PASS não definida.")
        sys.exit(1)

    print(f"--- Iniciando Configuração do KSC 16 em {host} ---")

    # Construção do arquivo de respostas (Answer File) para o KSC 16
    setup_cmds = [
        f"echo 'EULA_ACCEPTED=1' > /tmp/ksc_answers.txt",
        f"echo 'PP_ACCEPTED=1' >> /tmp/ksc_answers.txt",
        f"echo 'KSN_ACCEPTED=1' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_TYPE=PostgreSQL' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_INSTANCE=localhost' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_LOGIN=kluser' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DB_NAME=ksc' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_PORT=5432' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_PASSWORD={db_pass}' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_TYPE=PostgreSQL' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_INSTANCE=localhost' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_LOGIN=kluser' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DB_IAM_NAME=ksciam' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_PORT=5432' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_DBMS_IAM_PASSWORD={db_pass}' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_SERVERADDRESS={host}' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_IAM_ADDRESS=127.0.0.1' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_KLSVCUSER=ksc' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_KLADMINSGROUP=kladmins' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_KLIAMUSER=ksc' >> /tmp/ksc_answers.txt",
        f"echo 'KLSRV_UNATT_KLSRVUSER=ksc' >> /tmp/ksc_answers.txt",
        "sudo -E bash -c 'KLAUTOANSWERS=/tmp/ksc_answers.txt /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl'",
        "rm -f /tmp/ksc_answers.txt"
    ]

    results = run_ssh_commands_with_sudo(host, user, password, setup_cmds)

    if results:
        for res in results:
            print(f"\n[COMANDO]: {res['command']}")
            if res['stdout']: print(f"STDOUT: {res['stdout']}")
            if res['stderr']: print(f"STDERR: {res['stderr']}")
            print(f"STATUS: {res['exit_status']}")
            
            if res['exit_status'] != 0 and "postinstall.pl" in res['command']:
                print("\nFATAL: Falha na execução do postinstall.pl")
                sys.exit(1)
    
    print("\n--- Processo concluído ---")

if __name__ == "__main__":
    main()
