import yaml
import os
import re
import json
from openai import OpenAI
import random

OUTPUT_PATH = "./eng.json"

with open("./openai_secret.yaml", "r") as f:
    os.environ.update(yaml.safe_load(f))


client = OpenAI()


CODES = ['ES', 'BE', 'SA', 'FI', 'TW', 'DK', 'IN', 'AE', 'SE', 'AT', 'RU', 'NL',
         'IT', 'IL', 'AU', 'JP', 'FR', 'CH', 'HK', 'SG', 'DE', 'KR', 'CA', 'GB', 'CN', 'US']


def query():
    random.shuffle(CODES)
    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are a helpful assistant for classifying data."},
            {"role": "user", "content": (
                "Please classify the following list of ISO 3166-1 alpha-2 country codes into three categories:\n"
                "(1) Countries where it is clearly possible to live only with English\n"
                "(2) Countries where it is clearly not possible to live only with English\n"
                "(3) Countries that fall in between\n\n"
                "Please output the country codes for each category (1), (2), and (3) in the following format:\n"
                "(1): A, B, C\n"
                "(2): D, E, F\n"
                "(3): G, H, I\n\n"
                "Do not output anything except the above format.\n\n"
                f"Country codes: {', '.join(CODES)}"
            )}
        ]
    )
    return response.choices[0].message.content


def parse(x):
    r = {}
    x = x.split("\n")
    score_map = {0: 1, 1: 0, 2: 0.5}
    if len(x) != 3:
        return None
    for i in range(3):
        if not x[i].startswith(f"({str(i + 1)}): "):
            return None
        y = x[i].lstrip(f"({str(i + 1)}): ").split(",")
        y = [z.strip() for z in y]
        f = [re.match("^[A-Z]{2}$", z) for z in y]
        if not f:
            return None
        if not set(y).issubset(set(CODES)):
            return None
        r[score_map[i]] = set(y)

    if len(set(sum([list(x) for x in r.values()], []))) != len(CODES):
        return None
    return r


if __name__ == "__main__":
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "r") as f:
            scores = json.loads(f.read())
    else:
        scores = {k: 0 for k in CODES}

    trial = 100
    while True:
        r = parse(query())
        if not r:
            continue

        for score, ccs in r.items():
            for cc in ccs:
                scores[cc] += score

        with open(OUTPUT_PATH, "w") as f:
            json.dump(scores, f, indent=2)

        trial -= 1

        if trial <= 0:
            break
