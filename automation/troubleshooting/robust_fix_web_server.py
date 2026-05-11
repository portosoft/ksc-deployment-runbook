import paramiko
import os
import sys
import base64

def robust_fix_web_server(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        target_file = "/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js"
        
        # Read file
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {target_file}")
        stdin.write(password + '\n')
        stdin.flush()
        content = stdout.read().decode('utf-8')
        
        # Robust replace
        # Find the broken lines and replace them
        import re
        content = re.sub(r"runtime\.logger\.info\(DEBUG: openAPIServers", "runtime.logger.info('DEBUG: openAPIServers'", content)
        content = re.sub(r"runtime\.logger\.info\(DEBUG: serversCount", "runtime.logger.info('DEBUG: serversCount'", content)
        
        # Convert to base64 for safe transport
        b64_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # Write back using base64
        print("--- Writing fixed file via base64 ---")
        client.exec_command(f"echo '{b64_content}' > /tmp/web-server-b64.txt")
        client.exec_command(f"base64 -d /tmp/web-server-b64.txt > /tmp/web-server-fixed.js")
        stdin, stdout, stderr = client.exec_command(f"sudo -S cp /tmp/web-server-fixed.js {target_file}")
        stdin.write(password + '\n')
        stdin.flush()
        
        # Restart
        print("--- Restarting ---")
        client.exec_command("sudo -S systemctl restart KSCWebConsole.service")
        stdin.write(password + '\n')
        stdin.flush()
        
        print("Done!")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    
    robust_fix_web_server(host, user, password)
