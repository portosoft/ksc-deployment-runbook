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
with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# Find all occurrences of b'iam.users' or b'iam_users'
for target in [b'iam.users', b'iam_users']:
    start = 0
    while True:
        pos = data.find(target, start)
        if pos == -1:
            break
        print(f"Found {target} at position {pos}:")
        # Extract surrounding context (e.g. 200 bytes before and after)
        context = data[max(0, pos-400):min(len(data), pos+400)]
        # Filter printable characters
        printable = "".join(chr(b) if 32 <= b < 127 or b in (10, 13) else "." for b in context)
        print(printable)
        print("-" * 80)
        start = pos + len(target)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/search_bin_sql.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/search_bin_sql.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/search_bin_sql.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
