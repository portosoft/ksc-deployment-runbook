import paramiko
import os
import re
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

# Find all migration paths and their offsets
matches = list(re.finditer(rb'migrations/postgres/([0-9]+)_[a-zA-Z0-9_.-]+', data))
print(f"Total migration paths found in binary: {len(matches)}")

# Map each position in the binary to its containing/closest migration
def get_migration_for_pos(pos):
    closest = None
    closest_dist = 99999999
    # The migrations are embedded, usually the migration name is followed by the SQL content
    # or the SQL content is stored nearby. Let's find the nearest migration name *before* pos.
    for m in matches:
        m_start = m.start()
        if m_start <= pos:
            dist = pos - m_start
            if dist < closest_dist:
                closest_dist = dist
                closest = m.group(0).decode('ascii')
    return closest, closest_dist

keywords = [
    b'ui_locales',
    b'resources_schedule_pkey',
    b'ksc_directory_object_uniq_idx',
    b'workspace_id',
    b'deleting_outbox'
]

for kw in keywords:
    print(f"\\nKeyword: {kw.decode('ascii')}")
    kw_matches = list(re.finditer(kw, data))
    for kw_m in kw_matches:
        pos = kw_m.start()
        mig, dist = get_migration_for_pos(pos)
        if dist < 200000: # Only print if reasonably close to the migration headers
            # Let's extract 150 bytes of context
            context = data[max(0, pos-50):min(len(data), pos+150)]
            context_str = "".join(chr(b) if (32 <= b < 127 or b in (10, 13)) else "." for b in context)
            print(f"  Pos: {pos} | Mig: {mig} (dist={dist})")
            print(f"  Context: {context_str}")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/find_offending.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/find_offending.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/find_offending.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
