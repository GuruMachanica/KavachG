import glob, re

pages = [
    'Frontend/modules.html',
    'Frontend/demo.html',
    'Frontend/architecture.html',
    'Frontend/compliance.html',
    'Frontend/benchmarks.html'
]

for p in pages:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'navbar-inner' in c:
        print(f"Already updated {p}")
        continue

    # 1. Replace opening container + header
    c = re.sub(
        r'<body>\s*<div class="container">\s*(<!--.*?-->\s*)?<header class="navbar">',
        '<body>\n  <header class="navbar">\n    <div class="navbar-inner">',
        c
    )

    # 2. Close navbar-inner before </header> and open <main class="container">
    c = re.sub(
        r'(<a href="console\.html" class="btn-cta">[\s\S]*?</a>\s*)</header>',
        r'\1    </div>\n  </header>\n\n  <main class="container">',
        c
    )

    # 3. Replace footer opening
    c = re.sub(
        r'<footer>\s*<div class="footer-grid">',
        '</main>\n\n  <footer>\n    <div class="footer-inner">\n      <div class="footer-grid">',
        c
    )

    # 4. Replace footer closing
    c = re.sub(
        r'</footer>\s*</div>\s*(<!--.*?-->\s*)?<script',
        '</div>\n  </footer>\n\n  <script',
        c
    )

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Successfully converted {p} to edge-to-edge layout")
