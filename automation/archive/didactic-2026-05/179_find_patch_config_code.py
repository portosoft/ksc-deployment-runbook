import re


def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Search for "../actions/patch-config" or "patch-config"
    keywords = ["patch-config", "patchConfig", "Trusted servers"]

    for kw in keywords:
        print(f"\n=== SEARCHING FOR '{kw}' ===")
        for m in re.finditer(re.escape(kw), content):
            start = max(0, m.start() - 200)
            end = min(len(content), m.end() + 1000)
            snippet = content[start:end]
            cleaned = " ".join(snippet.split())
            print(f"[{m.start()}]: ... {cleaned} ...")
            print("-" * 50)


if __name__ == "__main__":
    main()
