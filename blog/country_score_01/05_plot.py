import json
import csv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    mapping = {}
    with open("./cc.csv", "r", encoding="UTF-8") as f:
        reader = csv.reader(f)
        for row in reader:
            mapping[row[1]] = row[0]

    ENG_PATH = "./eng.json"
    with open(ENG_PATH, "r") as f:
        scores = json.loads(f.read())

    counts = [(mapping[k], v, k) for k, v in scores.items()]
    counts = sorted(counts, key=lambda x: x[1])

    print(counts[::-1])

    def add_value_label(x_list, y_list):
        for i in range(0, len(x_list)):
            plt.text(y_list[i], i - 0.2, y_list[i])

    x = [c[0] for c in counts]
    y = [c[1] for c in counts]

    plt.figure(figsize=(10, 10), layout="tight", dpi=400)
    plt.barh(x, y)
    plt.title("English Levels")
    add_value_label(x, y)
    plt.savefig("english.png")
