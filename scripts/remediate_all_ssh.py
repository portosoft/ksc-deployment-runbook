import os
import re

def main():
    # Regular expression to match either AutoAddPolicy() or MissingHostKeyPolicy() with indentation
    target_pattern = re.compile(
        r"^(\s*)client\.set_missing_host_key_policy\(paramiko\.(?:AutoAddPolicy|MissingHostKeyPolicy)\(\)\)\s*$"
    )
    modified_count = 0

    for root, dirs, files in os.walk('.'):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in ['.git', '.pytest_cache', '.jules', 'venv', 'scratch']]
        for f in files:
            if f.endswith('.py'):
                fp = os.path.join(root, f)

                # Skip the remediation script itself
                if 'remediate_all_ssh.py' in fp:
                    continue

                # Read file
                with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()

                modified = False
                new_lines = []
                for line in lines:
                    match = target_pattern.match(line)
                    if match:
                        indent = match.group(1)
                        new_lines.append(f"{indent}client.load_system_host_keys()\n")
                        new_lines.append(f"{indent}client.set_missing_host_key_policy(paramiko.RejectPolicy())\n")
                        modified = True
                    else:
                        new_lines.append(line)

                if modified:
                    # Write modified content back
                    with open(fp, 'w', encoding='utf-8') as file:
                        file.writelines(new_lines)
                    modified_count += 1
                    print(f"Remediado: {fp}")

    print(f"Total de arquivos remediados: {modified_count}")

if __name__ == '__main__':
    main()
