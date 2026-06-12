import paramiko
import os
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        remote_script = """
import re

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# Search for iam.users
matches = list(re.finditer(rb'iam\.users', data, re.IGNORECASE))
print(f"Found {len(matches)} matches for iam.users")
for m in matches:
    pos = m.start()
    context = data[max(0, pos-100):min(len(data), pos+200)]
    printable = "".join(chr(b) if (32 <= b < 127 or b in (10, 13)) else "." for b in context)
    print(f"Pos {pos}:")
    print(printable)
    print("-" * 60)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/search_bin_users.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/search_bin_users.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/search_bin_users.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
