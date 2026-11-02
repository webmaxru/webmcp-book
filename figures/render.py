#!/usr/bin/env python3
"""Render figures/src/*.svg to manuscript/resources/images/*.png (2400 px wide) with headless Chromium.
Usage: python3 figures/render.py [figure-5-1 ...]   (no args = all)
Chromium: $CHROME, else Playwright's cached build, else google-chrome / chromium on PATH."""
import glob, os, re, shutil, subprocess, sys, tempfile, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "figures" / "src", ROOT / "manuscript" / "resources" / "images"
def chrome():
    if os.environ.get("CHROME"): return os.environ["CHROME"]
    c = sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")))
    if c: return c[-1]
    for n in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(n): return shutil.which(n)
    sys.exit("no Chromium found; set CHROME")
def size(svg):
    m = re.search(r'viewBox="\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)"', svg)
    return float(m.group(1)), float(m.group(2))
def render(path):
    svg = path.read_text(encoding="utf-8"); w, h = size(svg)
    scale = 2400 / w
    html = f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{(ROOT/"figures"/"figure.css").as_uri()}"></head><body>{svg}</body></html>'
    with tempfile.TemporaryDirectory() as td:
        page = pathlib.Path(td) / "f.html"; page.write_text(html, encoding="utf-8")
        out = OUT / (path.stem + ".png"); OUT.mkdir(parents=True, exist_ok=True)
        cmd = [chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
               "--allow-file-access-from-files", f"--force-device-scale-factor={scale}",
               f"--window-size={int(w)},{int(h)}", "--virtual-time-budget=3000",
               f"--screenshot={out}", page.as_uri()]
        subprocess.run(["timeout", "-k", "5", "60"] + cmd, check=True, capture_output=True)
    return out
if __name__ == "__main__":
    names = sys.argv[1:]
    files = [SRC / f"{n}.svg" for n in names] if names else sorted(SRC.glob("*.svg"))
    for f in files: print("rendered", render(f).relative_to(ROOT))
