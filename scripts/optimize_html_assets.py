import glob, re

for f in glob.glob('Frontend/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        c = file.read()

    # Add decoding="async" if not already present
    def add_async(match):
        tag = match.group(0)
        if 'decoding=' not in tag:
            tag = tag.replace('<img ', '<img decoding="async" ')
        if 'assets/cctv' in tag and 'loading=' not in tag:
            tag = tag.replace('<img ', '<img loading="lazy" ')
        return tag

    c = re.sub(r'<img\s+[^>]+>', add_async, c)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(c)

print("Applied image async decoding and lazy loading to all HTML pages.")
