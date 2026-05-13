import paramiko
import os
import sys

def check_node_ports_final(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check all node ports
        print("--- Node.js Listening Ports ---")
        stdin, stdout, stderr = client.exec_command("sudo -S ss -tulpn | grep node")
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        # Search for 8080 in systemd
        print("--- Searching for 8080 in systemd ---")
        stdin, stdout, stderr = client.exec_command("grep -r '8080' /etc/systemd/system/ 2>/dev/null")
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_node_ports_final(host, user, password)
