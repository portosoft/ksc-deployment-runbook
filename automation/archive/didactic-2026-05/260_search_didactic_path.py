import os


def main():
    root = r"c:\Antigravity\ksc-deployment-runbook"
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        for d in dirnames:
            if "didactic" in d.lower():
                found.append(os.path.join(dirpath, d))
        for f in filenames:
            if "didactic" in f.lower():
                found.append(os.path.join(dirpath, f))

    print("--- Search results for 'didactic' ---")
    for item in found:
        print(item)


if __name__ == "__main__":
    main()
