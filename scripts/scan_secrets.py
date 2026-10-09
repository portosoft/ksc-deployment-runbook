import os
import re

def main():
    # Regular expression to detect assignments to variables containing 'pass', 'secret', 'key', 'token', etc.
    # where the value is a non-empty string.
    secrets_pattern = re.compile(
        r'(\b\w*(?:password|passwd|ksc_pass|db_pass|secret|token|key|private_key)\w*)\s*=\s*([\'"])([^\'"]+)\2',
        re.IGNORECASE
    )

    # Also search for files containing 'password' or actual keys (like RSA PRIVATE KEY)
    private_key_pattern = re.compile(r'-----BEGIN\s+(?:RSA|OPENSSH|EC|DSA)?\s*PRIVATE\s+KEY-----', re.IGNORECASE)

    found_files = []

    for root, dirs, files in os.walk('scratch'):
        for f in files:
            if f.endswith('.py') or f.endswith('.txt') or f.endswith('.json') or f.endswith('.crt'):
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()

                    matches = []
                    # Check for assignments
                    for m in secrets_pattern.finditer(content):
                        var_name, quote, val = m.groups()
                        # Exclude harmless values
                        if len(val) > 3 and not val.startswith('%') and not val.startswith('$') and var_name.lower() not in ['key', 'token']:
                            matches.append((var_name, val))

                    # Check for private keys
                    if private_key_pattern.search(content):
                        matches.append(('PRIVATE_KEY_CONTENT', '***PRIVATE KEY***'))

                    if matches:
                        found_files.append((fp, matches))
                except Exception as e:
                    print(f"Error reading {fp}: {e}")

    print(f"Encontrados potenciais segredos em {len(found_files)} arquivos:")
    for fp, matches in found_files:
        print(f"\n{fp}:")
        for var, val in matches:
            print(f"  {var} = {val[:15]}...")

if __name__ == '__main__':
    main()
