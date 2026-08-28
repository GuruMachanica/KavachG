import os
import urllib.request


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


LIBS = [
    ("jspdf.umd.min.js", "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"),
    ("html2canvas.min.js", "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"),
    ("anime.min.js", "https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"),
    ("three.min.js", "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"),
    ("email.min.js", "https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"),
]



def main():
    libs_dir = os.path.join(os.path.dirname(__file__), "Frontend", "functions", "libs")
    ensure_dir(libs_dir)
    for filename, url in LIBS:
        dest = os.path.join(libs_dir, filename)
        try:
            print(f"Downloading {url} -> {dest}")
            urllib.request.urlretrieve(url, dest)
            print(f"Saved: {dest}")
        except Exception as e:
            print(f"Failed to download {filename}: {e}")


if __name__ == "__main__":
    main()

