import paramiko

import os
host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    print("Conexão bem sucedida!\n")
    
    cmd1 = f"echo '{password}' | sudo -S -u postgres psql -d ksciam -c \"SELECT table_schema, COUNT(*) AS total FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog','information_schema') GROUP BY table_schema ORDER BY table_schema;\""
    
    cmd2 = """
    for svc in kladminserver_srv kliam_srv KSCSvcWebConsole KSCWebConsole; do
      echo "$svc: $(systemctl is-active $svc 2>/dev/null)"
    done
    """
    
    cmd3 = "echo | openssl s_client -connect 127.0.0.1:13299 -brief 2>/dev/null | head -3"
    
    for i, cmd in enumerate([cmd1, cmd2, cmd3], 1):
        print(f"=== PARTE 1.{i} ===")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        if out: print(out)
        if err: print(f"STDERR: {err}")
        print("\n")

except Exception as e:
    print(f"Erro: {e}")
finally:
    client.close()
