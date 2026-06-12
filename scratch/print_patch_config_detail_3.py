def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Print a window around index 1133000 to 1134500
    start = 1133000
    end = 1134500
    print(content[start:end])

if __name__ == "__main__":
    main()
