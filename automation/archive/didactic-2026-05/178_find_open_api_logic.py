import re


def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Search for openAPIServers, pools, trusted servers, server address, port 13000, 13299
    keywords = [
        "openAPIServers",
        "pools",
        "Trusted servers",
        "13000",
        "13299",
        "adminServer",
    ]

    print("--- Searching for OpenAPI / server pool logic ---")
    for kw in keywords:
        pattern = re.compile(r".{0,150}" + re.escape(kw) + r".{0,150}", re.IGNORECASE)
        matches = pattern.findall(content)
        print(f"Keyword '{kw}': {len(matches)} matches")
        for m in matches[:3]:
            cleaned = " ".join(m.split())
            print(f"  Match: {cleaned}")


if __name__ == "__main__":
    main()
