import yaml
import shutil

def prepare(path):
    #shutil.copy(path, f'_{path}')

    with open(path, "r", encoding="utf-8") as f:
        ls = yaml.safe_load(f)
    
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(ls, f, allow_unicode=True)

    return ls

with open("./tmp_cv.html", "r", encoding="utf-8") as f:
    tmp = f.read()

hl = prepare("highlights.yaml")
ps = prepare("profile.yaml")


def profile():
    print(ps)
    html = ""
    for section in ps:
        for header, vs in section.items():
            html += f'<h2>{header}</h2><table class="profile">'
            for v in vs:
                for k, v in v.items():
                    v = v.replace("#JP#", '<span class="fi fi-jp fi-bordered"></span>')
                    html += f'<tr><td>{k}</td><td>{v}</td></tr>'
            html += '</table>'
    return html


def highlights():
    html = ""

    for section in hl:
        if section["emph"]:
            html += '<details open>'
        else:
            html += '<details>'
        
        html += f'<summary>{section["header"]}<span class="period">{section["period"]}</span></summary>'

        if isinstance(section["text"]["en"], list):
            html += '<ul>'
            for sent in section["text"]["en"]:
                html += f'<li>{sent}</li>'
            html += '</ul>'
        else:
            html += f'{section["text"]["en"]}'

        for lang in section["ref"].keys():
            html += f'<details{" open" if lang == "en" else ""}><summary>References in {lang}</summary><ol>'
            for ref in section["ref"][lang]:
                html += f'<li>{ref.replace("佐藤怜", "<u>佐藤怜</u>").replace("Rei Sato", "<u>Rei Sato</u>")}</li>'
            html += '</ol></details>'
        html += '</details>'
    return html

html = profile()
tmp = tmp.replace("### PROFILE ###", html)
html = highlights()
tmp = tmp.replace("### HIGHLIGHTS ###", html)

with open("./cv.html", "w", encoding="utf-8") as f:
    f.write(tmp)