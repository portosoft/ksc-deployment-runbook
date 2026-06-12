import paramiko
import os
import json
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    # Load credentials from .env to test
    admin_name = os.getenv("KSC_ADMIN_NAME")
    admin_pass = os.getenv("KSC_ADMIN_PASS")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Python script to run on the remote host to test OpenAPI login
        test_script = """
import urllib.request, urllib.error, base64, ssl, json

ctx = ssl._create_unverified_context()
SRV = "https://127.0.0.1:13299"

combinations = [
    ("kscadmin2", "[REDACTED_KSC_ADMIN2_PASS]"),
    ("kscadmin", "[REDACTED_KSC_ADMIN2_PASS]"),
    ("kscadmin", "[REDACTED_KSC_ADMIN_PASS]"),
    ("KLAdmins", "[REDACTED_KSC_ADMIN_PASS]"),
    ("KLAdmins", "[REDACTED_KSC_ADMIN2_PASS]"),
    ("suporte", "[REDACTED_SSH_PASS]"),
    ("suporte", "[REDACTED_KSC_ADMIN_PASS]"),
    ("kscadmin", "[REDACTED_ADMIN_PASS]"),
]

for u, p in combinations:
    u64 = base64.b64encode(u.encode()).decode()
    p64 = base64.b64encode(p.encode()).decode()
    headers = {
        "Authorization": f'KSCBasic user="{u64}", pass="{p64}", internal="1"',
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(f"{SRV}/api/v1.0/login", data=b"{}", headers=headers, method="POST")
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=5)
        print(f"[SUCCESS] User: {u} | Pass: {p} -> HTTP {r.status}")
        print("Response Headers:", dict(r.headers))
    except urllib.error.HTTPError as e:
        print(f"[FAILED] User: {u} | Pass: {p} -> HTTP {e.code}")
        print("Response Headers:", dict(e.headers))
    except Exception as e:
        print(f"[ERROR] User: {u} | Pass: {p} -> {e}")
"""
        # Save test script on server
        stdin, stdout, stderr = client.exec_command(
            "cat > /tmp/test_login_combinations.py"
        )
        stdin.write(test_script)
        stdin.close()
        stdout.read()
        stderr.read()

        # Run test script
        print("Running login combinations test on server...")
        stdin, stdout, stderr = client.exec_command(
            "python3 /tmp/test_login_combinations.py"
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
