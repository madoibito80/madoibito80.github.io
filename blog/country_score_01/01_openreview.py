import urllib.parse
import requests
import json
import os
import time


INDEX_BASE_URL = "https://api*.openreview.net/notes"
PAGE_SIZE = 100
ONLY_FIRST_AUTHOR = True
PROFILE_BASE_URL = "https://openreview.net/profile"
CONF = [('NeurIPS+2022+Accept', 1),
        ('NeurIPS 2023 oral', 2),
        ('NeurIPS 2023 spotlight', 2),
        ('NeurIPS 2023 poster', 2),
        ('NeurIPS 2024 oral', 2),
        ('NeurIPS 2024 spotlight', 2),
        ('NeurIPS 2024 poster', 2)]


def get_authors(venue, api_version):
    authors = []
    for npage in range(99999):
        params = {"content.venue": venue,
                  "limit": PAGE_SIZE, "offset": npage * PAGE_SIZE}
        query_str = "&".join(f"{k}={v}" for k, v in params.items())
        endpoint = INDEX_BASE_URL.replace(
            "*", "") if api_version == 1 else INDEX_BASE_URL.replace("*", "2")
        url = endpoint + "?" + query_str
        papers = json.loads(requests.get(url).text)["notes"]

        print(f"Processing {url}, n={len(papers)}")

        if len(papers) == 0:
            break

        for paper in papers:
            paper = paper["content"]
            if "authorids" not in paper:
                continue

            if api_version == 1:
                _authors = paper["authorids"]
            else:
                _authors = paper["authorids"]["value"]

            if ONLY_FIRST_AUTHOR:
                _authors = _authors[:1]

            authors += _authors
    return authors


def get_affiliation(author):
    params = {}
    if author.startswith("~"):
        params["id"] = author
    elif "@" in author:
        params["email"] = author
    else:
        raise ValueError

    query_str = urllib.parse.urlencode(params)
    url = PROFILE_BASE_URL + "?" + query_str
    print(f"Processing {url}")
    try:
        res = requests.get(url).text
        res = res.split(
            '<script id="__NEXT_DATA__" type="application/json">')[1]
        res = res.split('</script>')[0]
        res = json.loads(res)
        hist = res["props"]["pageProps"]["profile"]["history"][0]
        hist = hist["institution"]
        hist["author"] = author
        print(f"Result: {hist}")
        return hist
    except:
        pass
    return None


if __name__ == "__main__":
    # fetch authors
    for venue, api_version in CONF:
        output_path = f"./authors/{venue.replace(' ', '')}.csv"
        if os.path.exists(output_path):
            print(f"Skipping due to an existing result on {venue}.")
            continue

        authors = get_authors(venue, api_version)
        with open(output_path, "w", encoding="UTF-8") as f:
            f.write("\n".join(authors))

    # fetch affiliations
    for venue, _ in CONF:
        output_path = f"./affiliations/{venue.replace(' ', '')}.json"
        if os.path.exists(output_path):
            print(f"Skipping due to an existing result on {venue}.")
            continue

        input_path = f"./authors/{venue.replace(' ', '')}.csv"
        with open(input_path, "r", encoding="UTF-8") as f:
            authors = f.read().split("\n")

        affs = []
        for author in authors:
            for _ in range(3):
                time.sleep(1)
                aff = get_affiliation(author)
                if aff is None:
                    time.sleep(5)
                else:
                    affs.append(aff)
                    break

        with open(output_path, "w", encoding="UTF-8") as f:
            json.dump(affs, f, indent=2)
