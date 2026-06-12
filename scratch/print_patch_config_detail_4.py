def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Print a window around index 1134300 to 1135300
    start = 1134300
    end = 1135300
    print(content[start:end])

if __name__ == "__main__":
    main()
