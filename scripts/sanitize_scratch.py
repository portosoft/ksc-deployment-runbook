import os
import re

def main():
    host_pattern = re.compile(r"^(\s*)(hostname|host)\s*=\s*([\'\"])(?:kscserver\.tail8b9ae\.ts\.net|192\.168\.\d+\.\d+)\3\s*$", re.MULTILINE)
    user_pattern = re.compile(r"^(\s*)username\s*=\s*([\'\"])suporte\2\s*$", re.MULTILINE)
    pass_pattern = re.compile(r"^(\s*)password\s*=\s*([\'\"])p1WuCxrARN9WR0U0Meq4xmi\*QUsI\^#aZ\2\s*$", re.MULTILINE)

    modified_count = 0

    for root, dirs, files in os.walk('scratch'):
        for f in files:
            if f.endswith('.py'):
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()

                    modified = False

                    # Replace host
                    new_content, count_h = host_pattern.subn(r"\1\2 = os.getenv('KSC_HOST')", content)
                    if count_h > 0:
                        modified = True
                        content = new_content

                    # Replace user
                    new_content, count_u = user_pattern.subn(r"\1username = os.getenv('KSC_USER')", content)
                    if count_u > 0:
                        modified = True
                        content = new_content

                    # Replace password
                    new_content, count_p = pass_pattern.subn(r"\1password = os.getenv('KSC_PASS')", content)
                    if count_p > 0:
                        modified = True
                        content = new_content

                    if modified:
                        # Ensure 'import os' is present at the top of the file
                        if 'import os' not in content:
                            content = "import os\n" + content

                        with open(fp, 'w', encoding='utf-8') as file:
                            file.write(content)

                        modified_count += 1
                        print(f"Sanitizado: {fp}")
                except Exception as e:
                    print(f"Error processing {fp}: {e}")

    print(f"Total de arquivos de rascunho sanitizados: {modified_count}")

if __name__ == '__main__':
    main()
