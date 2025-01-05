import json
import os
import csv
import matplotlib.pyplot as plt
from collections import Counter


def count_cc():
    MAPPING_PATH = "./map.json"
    with open(MAPPING_PATH, "r") as f:
        mapping = json.loads(f.read())

    codes = []
    acc = [0, 0]

    ls = os.listdir("./affiliations")
    for venue in ls:
        with open(f"./affiliations/{venue}", "r") as f:
            js = json.loads(f.read())
            for x in js:
                if "country" in x:
                    gt = x["country"]
                else:
                    gt = None
                if "domain" in x:
                    aff = f'{x["name"]} ({x["domain"]})'
                else:
                    aff = x["name"]

                cc = mapping[aff]
                if gt is not None:
                    acc[1] += 1
                    if gt == cc:
                        acc[0] += 1
                    cc = gt
                codes.append(cc)

    print(f"Accuracy of GPT: {round(acc[0] / acc[1], 3)}")
    return Counter(codes)


def convert_country(counts):
    mapping = {}
    with open("../cc.csv", "r", encoding="UTF-8") as f:
        reader = csv.reader(f)
        for row in reader:
            mapping[row[1]] = row[0]

    _counts = []
    for k, v in counts:
        _counts.append((mapping[k], v, k))

    return _counts


if __name__ == "__main__":
    counts = count_cc()
    thr = float(counts["JP"]) * 0.1
    counts = [(k, v) for k, v in counts.items() if v >= thr]
    counts = sorted(counts, key=lambda x: x[1])

    print(f"List of Country Codes: {[x[0] for x in counts]}")
    counts = convert_country(counts)

    print(counts[::-1])

    def add_value_label(x_list, y_list):
        for i in range(0, len(x_list)):
            plt.text(y_list[i], i - 0.2, y_list[i])

    x = [c[0] for c in counts]
    y = [c[1] for c in counts]

    plt.figure(figsize=(10, 10), layout="tight", dpi=400)
    plt.barh(x, y)
    plt.title("NeurIPS 2022-24 First Authors by Country")
    add_value_label(x, y)
    plt.savefig("NeurIPS.png")
