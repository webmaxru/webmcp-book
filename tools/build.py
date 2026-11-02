#!/usr/bin/env python3
"""One entry point for every edition of the book.

    python3 tools/build.py [pdf|epub|site|zip|all] [--manuscript manuscript] [--version X.Y.Z]

  site  web edition -> dist/site/ (copies staticwebapp.config.json into it when the file exists)
  zip   web edition zipped -> dist/<html_zip_stem>-v<version>.zip (builds the site first)
  pdf   print PDF -> dist/<file_stem>-v<version>.pdf (7 x 9.25 in; needs Chromium via Playwright)
  epub  EPUB 3 -> dist/<file_stem>-v<version>.epub
  all   site + zip + epub + pdf (the default)

The build reads only manuscript/, tools/book.json, CHANGELOG.md (release history) and theme/.
--version (or $BOOK_VERSION) overrides "version" in tools/book.json for one build; the release
workflow sets it from the tag. Each step prints its time; the run ends with a summary.
"""
import argparse, os, pathlib, sys, time, zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bookmd  # noqa: E402

def zip_site(site_dir, cfg):
    out = bookmd.ROOT / "dist" / f'{cfg["html_zip_stem"]}-v{bookmd.book_version(cfg)}.zip'
    out.parent.mkdir(parents=True, exist_ok=True)
    top = f'{cfg["html_zip_stem"]}-v{bookmd.book_version(cfg)}'
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(pathlib.Path(site_dir).rglob("*")):
            if f.is_file() and f.name != "staticwebapp.config.json":
                z.write(f, f"{top}/{f.relative_to(site_dir)}")
    print(f"zip: {out} ({out.stat().st_size / 1048576:.1f} MB); open {top}/index.html", flush=True)
    return out

def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the book's editions from the manuscript.")
    ap.add_argument("target", nargs="?", default="all", choices=["pdf", "epub", "site", "zip", "all"])
    ap.add_argument("--manuscript", default=str(bookmd.MANUSCRIPT))
    ap.add_argument("--version", default=None, help="override tools/book.json version for this build")
    ap.add_argument("--chrome", default=None, help="Chromium/Chrome binary for the PDF (default: $CHROME_PATH or Playwright's)")
    a = ap.parse_args(argv)
    if a.version:
        os.environ["BOOK_VERSION"] = a.version
    cfg = bookmd.load_config()
    ms = pathlib.Path(a.manuscript)
    timings = []
    def step(name, fn):
        t = time.time()
        r = fn()
        timings.append((name, time.time() - t, r))
        print(f"[{name}] done in {time.time() - t:.1f} s", flush=True)
        return r
    targets = ["site", "zip", "epub", "pdf"] if a.target == "all" else [a.target]
    site_dir = bookmd.ROOT / "dist" / "site"
    for tg in targets:
        if tg == "site":
            import build_site
            step("site", lambda: build_site.build(ms, site_dir))
        elif tg == "zip":
            if not (site_dir / "index.html").exists() or "site" not in targets:
                import build_site
                step("site", lambda: build_site.build(ms, site_dir))
            step("zip", lambda: zip_site(site_dir, cfg))
        elif tg == "epub":
            import build_epub
            step("epub", lambda: build_epub.build(ms, None))
        elif tg == "pdf":
            import build_pdf
            step("pdf", lambda: build_pdf.build(ms, None, chrome=a.chrome))
    print("\nsummary (version " + bookmd.book_version(cfg) + "):")
    for name, secs, r in timings:
        print(f"  {name:<5} {secs:7.1f} s  {r}")

if __name__ == "__main__":
    main()
