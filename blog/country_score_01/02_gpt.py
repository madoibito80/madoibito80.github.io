import yaml
import os
import re
import json
import time
from openai import OpenAI
from collections import Counter

MAPPING_PATH = "./map.json"

with open("../openai_secret.yaml", "r") as f:
    os.environ.update(yaml.safe_load(f))


client = OpenAI()


def query_code(org):
    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        temperature=0.4,
        messages=[
            {"role": "system", "content": """
            You are a helpful assistant designed to output ISO 3166-1 alpha-2 country codes.
            Do not output anything except country codes."""},
            {"role": "user", "content": f"What is the country code for the country where {
                org} is located?"}
        ]
    )
    return response.choices[0].message.content


def load_affiliation_list():
    ls = os.listdir("./affiliations")
    affs = []
    for l in ls:
        with open(f"./affiliations/{l}", "r") as f:
            js = json.loads(f.read())
            for x in js:
                if "domain" in x:
                    aff = f'{x["name"]} ({x["domain"]})'
                else:
                    aff = x["name"]
                affs.append(aff)

    affs = list(set(affs))
    return affs


if __name__ == "__main__":
    if os.path.exists(MAPPING_PATH):
        with open(MAPPING_PATH, "r") as f:
            mapping = json.loads(f.read())
    else:
        mapping = {}

    affs = load_affiliation_list()
    print(f"Num of total affiliations: {len(affs)}")
    affs = list(set(affs) - set(mapping.keys()))
    print(f"Num of affiliations to query: {len(affs)}")

    for aff in affs:
        codes = []
        while True:
            code = query_code(aff)
            r = re.match("^[A-Z]{2}$", code)
            if r:
                codes.append(code)
            else:
                time.sleep(1)
            counter = Counter(codes)
            if 2 in counter.values():
                break

        mapping[aff] = [k for k, v in counter.items() if v >= 2][0]
        print(f"{aff}: {code}")

        with open(MAPPING_PATH, "w") as f:
            json.dump(mapping, f, indent=2)
