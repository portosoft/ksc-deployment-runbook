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

# We look for all migration file names
matches = re.finditer(rb'migrations/postgres/[a-zA-Z0-9_.-]+', data)
migrations = []
for m in matches:
    migrations.append((m.start(), m.end(), m.group(0).decode('ascii')))

print(f"Found {len(migrations)} migration references.")

keywords = [b'ui_locales', b'resources_schedule_pkey', b'ksc_directory_object_uniq_idx', b'workspace_id', b'deleting_outbox']

# For each keyword, let's find where it occurs in the binary and see which migration it belongs to
for kw in keywords:
    print(f"\\n=== Matches for keyword: {kw.decode('ascii')} ===")
    kw_matches = list(re.finditer(kw, data))
    print(f"Found {len(kw_matches)} occurrences in binary.")
    for kw_m in kw_matches:
        pos = kw_m.start()
        # Find the closest migration filename before this position, or search within a window of 10KB
        closest_mig = None
        closest_dist = 9999999
        for start, end, name in migrations:
            if start < pos:
                dist = pos - start
                if dist < closest_dist:
                    closest_dist = dist
                    closest_mig = name
            else:
                dist = start - pos
                if dist < closest_dist:
                    closest_dist = dist
                    closest_mig = name

        print(f"Occurrence at {pos} (closest migration: {closest_mig}, dist={closest_dist}):")
        # Print a chunk of context around the occurrence
        chunk = data[max(0, pos-200):min(len(data), pos+600)]
        printable = "".join(chr(b) if (32 <= b < 127 or b in (10, 13)) else "." for b in chunk)
        print(printable)
        print("-" * 50)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/extract_failed_migrations_sql.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command(
            "python3 /tmp/extract_failed_migrations_sql.py"
        )
        print(stdout.read().decode("utf-8", errors="replace"))

        client.exec_command("rm -f /tmp/extract_failed_migrations_sql.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
