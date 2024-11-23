import yaml
import json

with open("./highlights.yaml", "r", encoding="utf-8") as f:
    hl = yaml.safe_load(f)

print(json.dumps(hl, indent=4))

with open("./tmp_cv.html", "r", encoding="utf-8") as f:
    tmp = f.read()

html = ""
for section in hl:
    if section["emph"]:
        html += '<details open>'
    else:
        html += '<details>'
    
    html += f'<summary>{section["header"]}<span class="period">{section["period"]}</span></summary>'
    html += f'{section["text"]["en"]}'

    for lang in section["ref"].keys():
        html += f'<details{" open" if lang == "en" else ""}><summary>References in {lang}</summary><ol>'
        for ref in section["ref"][lang]:
            html += f'<li>{ref}</li>'
        html += '</ol></details>'
    html += '</details>'

tmp = tmp.replace("### HIGHLIGHTS ###", html)
with open("./cv.html", "w", encoding="utf-8") as f:
    f.write(tmp)