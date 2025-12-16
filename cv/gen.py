import yaml
import shutil

def prepare(path):
    #shutil.copy(path, f'_{path}')

    with open(path, "r", encoding="utf-8") as f:
        ls = yaml.safe_load(f)
    
    #with open(path, "w", encoding="utf-8") as f:
    #    yaml.safe_dump(ls, f, allow_unicode=True)

    return ls

with open("./tmp_cv.html", "r", encoding="utf-8") as f:
    tmp = f.read()

hl = prepare("highlights.yaml")
ps = prepare("profile.yaml")
bs = prepare("blog.yaml")
ss = prepare("skills.yaml")

def flag(x):
    return x.replace("${JP}", '<span class="fi fi-jp fi-bordered"></span>')

def profile():
    html = ""
    for section in ps:
        html += f'<h2>{section["label"]}</h2>'
        html += '<table class="profile">'
        for org in section["organizations"]:
            html += f'<tr><td>{flag(org["label"])}</td><td>'
            for role in org["roles"]:
                html += f'<div class="role">{role["label"]}'
                if "highlights" in role:
                    listr = ''.join([f'<li>{x}</li>' for x in role["highlights"]])
                    html += f'<ul>{listr}</ul>'
                html += '</div>'
            html += '</td></tr>'
        html += '</table>'
    return html

def skills(ss):
    html = ""
    html += '<table class="profile">'
    for section in ss:
        html += f'<tr><td>{section["label"]}</td><td><ul>'
        html += "".join([f'<li>{x}</li>' for x in section["marks"]])
        html += '</ul></td></tr>'
    html += '</table>'
    return html


def blog(bs):
    html = ''
    for lang in ["en", "ja"]:
        if lang == "ja":
            html += '<details class="blind"><summary>in ja</summary>'
        html += '<table class="blog">'
        for blog in bs[lang]:
            html += f'<tr><td>{blog["date"]}</td><td>{blog["link"]}</td></tr>'
        html += '</table>'
    html += '</details>'
    return html

def highlights():
    html = ""

    for section in hl:
        if section["emph"]:
            html += '<details open>'
        else:
            html += '<details>'
        
        html += f'<summary class="heading">{section["header"]}<span class="period">{section["period"]}</span></summary>'

        if isinstance(section["text"]["en"], list):
            html += '<ul>'
            for sent in section["text"]["en"]:
                html += f'<li>{sent}</li>'
            html += '</ul>'
        else:
            html += f'{section["text"]["en"]}'

        for lang in section["ref"].keys():
            html += f'<details{" open" if lang == "en" else " class=\"blind\""}><summary>Publications in {lang}</summary><ol>'
            for ref in section["ref"][lang]:
                html += f'<li>{ref.replace("佐藤怜", "<u>佐藤怜</u>").replace("Rei Sato", "<u>Rei Sato</u>")}</li>'
            html += '</ol></details>'
        html += '</details>'
    return html

html = profile()
tmp = tmp.replace("${PROFILE}", html)
html = highlights()
tmp = tmp.replace("${HIGHLIGHTS}", html)
html = blog(bs)
tmp = tmp.replace("${BLOG}", html)
html = skills(ss)
tmp = tmp.replace("${SKILLS}", html)

with open("./cv.html", "w", encoding="utf-8") as f:
    f.write(tmp)