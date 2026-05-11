import paramiko
import os
import sys
import json

def fix_web_console_with_certs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=60)
        
        # 1. Generate Dummy Certs
        print("--- Generating certificates ---")
        client.exec_command('openssl req -x509 -newkey rsa:2048 -keyout /tmp/key.pem -out /tmp/cert.pem -days 365 -nodes -subj "/CN=kscserver"')
        client.exec_command('sudo -S cp /tmp/key.pem /tmp/cert.pem /var/opt/kaspersky/ksc-web-console/')
        stdin, _, _ = client.exec_command('sudo -S chown ksc:kladmins /var/opt/kaspersky/ksc-web-console/*.pem')
        stdin.write(password + '\n')
        stdin.flush()

        # 2. Configuration JSON v4
        config = {
            "acceptEula": True,
            "address": "127.0.0.1",
            "port": "13299",
            "defaultLangId": 1046,
            "enableLog": True,
            "trusted": True,
            "certDomain": "kscserver.tail8b9ae.ts.net",
            "certPath": "/var/opt/kaspersky/ksc-web-console/cert.pem",
            "keyPath": "/var/opt/kaspersky/ksc-web-console/key.pem",
            "additionalLocale": "",
            "installFolder": "/var/opt/kaspersky/ksc-web-console",
            "webConsoleAccount": "ksc:kladmins",
            "serviceWebConsoleAccount": "ksc:kladmins",
            "pluginAccount": "ksc:kladmins",
            "managementServiceAccount": "ksc:kladmins",
            "natsMessageQueueAccount": "ksc:kladmins"
        }
        
        json_content = json.dumps(config, indent=2)
        
        # 3. Upload JSON
        print("--- Uploading setup-v4.json ---")
        client.exec_command(f"echo '{json_content}' > /tmp/web-setup-v4.json")
        
        # 4. Run Setup
        print("--- Running setup.js v4 ---")
        cmd = "cd /var/opt/kaspersky/ksc-web-console && sudo -S ./node setup.js /tmp/web-setup-v4.json"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + '\n')
        stdin.flush()
        
        print(f"STDOUT:\n{stdout.read().decode('utf-8')}")
        print(f"STDERR:\n{stderr.read().decode('utf-8')}")
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    
    fix_web_console_with_certs(host, user, password)
