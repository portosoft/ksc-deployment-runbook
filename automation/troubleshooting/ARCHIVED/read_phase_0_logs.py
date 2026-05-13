import paramiko
import os
import sys

def read_phase_0_logs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read logs
        print("--- KSC-Service-Web-Console Log (Tail 100) ---")
        cmd1 = "sudo -S tail -n 100 /var/opt/kaspersky/ksc-web-console/logs/KSC-Service-Web-Console-server.kscserver.tail8b9ae.ts.net.2026-05-11.log"
        stdin, stdout, stderr = client.exec_command(cmd1)
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        print("\n--- KSC-Web-Console Log (Tail 100) ---")
        cmd2 = "sudo -S tail -n 100 /var/opt/kaspersky/ksc-web-console/logs/KSC-Web-Console-server.kscserver.tail8b9ae.ts.net.2026-05-11.log"
        stdin, stdout, stderr = client.exec_command(cmd2)
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    read_phase_0_logs(host, user, password)
