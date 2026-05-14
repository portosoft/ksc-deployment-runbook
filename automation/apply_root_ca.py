import sys
import os
import paramiko

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)
    for cmd in commands:
        print(f"--- {cmd} ---")
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        stdin.write(password + '\n')
        stdin.flush()
        out = stdout.read().decode('utf-8', errors='ignore')
        if out: print(out.encode('ascii', 'backslashreplace').decode('ascii'))
    client.close()

secrets = vault.decrypt_secrets()

root_ca = """-----BEGIN CERTIFICATE-----
MIIDGjCCAgKgAwIBAgITZk0WzBRzlZETSymcN4L/kYKyxzANBgkqhkiG9w0BAQsF
ADAWMRQwEgYDVQQDDAtLU0MgUm9vdCBDQTAeFw0yNjA0MTEyMDEyMjBaFw0yNzA1
MTMyMDEyMjBaMBYxFDASBgNVBAMMC0tTQyBSb290IENBMIIBIjANBgkqhkiG9w0B
AQEFAAOCAQ8AMIIBCgKCAQEA+Q7+bWZOk8FBN5iytqZZmdSP3zeyylTlOHOD1GK4
YUFlDytpiNxnjdjan8V+qKqIo/g8OSdaOInXx0lE25z8HKP8I6t5q1igjLq3bSzP
+rVkTx1hN0kYjfdTYtx9YRPtQPTtj/09JcHV1kibl9Bepmf1CFvGuhQivq+P/O0/
5RczL53iCTj3XZ+p1dBPjxvgd/1OUh0xPyw/ZqDANvD0inxhKqApidNkNSfePV7p
GTxyj7wFnF9Oi7ORvIxNrpzfUYx0p/qUJb96VeQy/uOe08aGekYquQC8DSQRL6DQ
2aW58dcyCHWzDawC5O+Y5TL7sXyrW3zNkIWgkV4MfXMR7wIDAQABo2EwXzALBgNV
HQ8EBAMCAaYwHQYDVR0OBBYEFOAcp0ErFLqr/teEbHHyNfevzaa/MBIGA1UdEwEB
/wQIMAYBAf8CAQEwHQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMA0GCSqG
SIb3DQEBCwUAA4IBAQCxoekSKjTCk00W3deTgIo7ixNNoxsVKod5glbnB6PIFDz0
tCtLq47JFTGwpEB1HRNW7j8f+ji5Bho+sOYwBJb+nJCmlRw/4vBsEyGfcpP4U1l4
Gt3vvepFRF86rAholghpIufzWCsa3PrMyQEhitMDtOQR3A0MJ5NG7D/XAIZmIVI9
+f46IG6q0Q1AzRnX+H0amhB4NSKTl3v1E7ry4P393th8rQ/yoO3NzNljyZ6IbqGC
hT5IohOpx3TUURy0r5uK+1oYUFnBI9sP4ARwucJFJN96gpItZxbHO91TISyvNMbC
4f8ZEdvnFhdscZQuhFA2xuWijg4bxzTjfm55Qwsl
-----END CERTIFICATE-----
"""

cmds = [
    f"echo '{root_ca}' | sudo tee /var/opt/kaspersky/ksc-web-console/ksc_root_ca.pem",
    "chown root:root /var/opt/kaspersky/ksc-web-console/ksc_root_ca.pem",
    "chmod 644 /var/opt/kaspersky/ksc-web-console/ksc_root_ca.pem",
    "sed -i 's|NODE_EXTRA_CA_CERTS=.*|NODE_EXTRA_CA_CERTS=/var/opt/kaspersky/ksc-web-console/ksc_root_ca.pem|' /etc/systemd/system/ksc-web-console.service",
    "systemctl daemon-reload",
    "systemctl restart ksc-web-console"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], cmds)
