with open("./index.md", "r") as f:
    rows = f.readlines()

html = """
<!DOCTYPE html>
<html>
  <head>
    <title>40+ Web Agent Benchmarks for Evaluating GUI Understanding and Manipulation Abilities</title>
    <link rel="stylesheet" href="../sakura.css" />
    <link rel="stylesheet" href="../../common/prism.css" />
  </head>
  <body>
    <script src="../../common/prism.js"></script>

    <div style="text-align: center">
      <h2>40+ Web Agent Benchmarks for Evaluating GUI Understanding and Manipulation Abilities</h2>
      Rei Sato<br />Mar. 2025
    </div>
"""

in_ul = False
for row in rows:
    if row.startswith("#"):
        if in_ul:
            html += "</ul>"
            in_ul = False
        lv = str(row.count("#")*2)
        html += f"<h{lv}>{row.lstrip("#").strip()}</h{lv}>"
    elif row.startswith("-"):
        if not in_ul:
            html += "<ul>"
            in_ul = True
        html += f"<li>{row.lstrip("-").strip()}</li>"
    else:
        if in_ul:
            html += "</ul>"
            in_ul = False
        html += row

if in_ul:
    html += "</ul>"
    in_ul = False
html += "</body></html>"

with open("./index.html", "w") as f:
    f.write(html)