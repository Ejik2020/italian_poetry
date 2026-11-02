"""Check rendered book links with exact Unicode/case spelling, using stdlib only."""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attr in ("href", "src", "poster"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "_book").resolve()
    files = {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}
    pages = {name: Page(p.read_text()) for name, p in files.items() if p.suffix == ".html"}
    errors = []
    # The chapter list is deliberately one filename per line in _quarto.yml.
    config = Path("_quarto.yml").read_text()
    chapters = re.findall(r"^    - (.+\.qmd)\s*$", config, re.M)
    expected = {str(Path(ch).with_suffix(".html")) for ch in chapters}
    for chapter in chapters:
        source = Path(chapter).read_text()
        name = str(Path(chapter).with_suffix('.html'))
        if name not in files:
            continue
        originals = len(re.findall(r'^:::.*italian', source, re.M))
        paired = files[name].read_text().count('data-paired="true"')
        if originals != paired:
            errors.append(f'{name}: {originals} supplied originals but {paired} rendered poem pairs')
    for name in sorted(expected - pages.keys()):
        errors.append(f"Missing chapter: {name}")
    for name in sorted(pages.keys() - expected):
        errors.append(f"Unexpected rendered page: {name}")
    for name, page in pages.items():
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            if path.startswith("/"):
                errors.append(f"{name}: root-relative link breaks repository subpath: {link}")
                continue
            target = (root / Path(name).parent / path).resolve() if path else root / name
            if target.is_dir():
                target /= "index.html"
            try:
                relative = target.relative_to(root).as_posix()
            except ValueError:
                errors.append(f"{name}: link escapes output: {link}")
                continue
            if relative not in files:
                errors.append(f"{name}: missing target (including case): {link}")
            elif url.fragment and relative in pages and unquote(url.fragment) not in pages[relative].ids:
                errors.append(f"{name}: missing fragment: {link}")
    for name, p in files.items():
        if p.suffix != ".css":
            continue
        for link in re.findall(r"url\(\s*['\"]?([^)'\"]+)", p.read_text()):
            url = urlsplit(link.strip())
            if url.scheme or url.netloc or not url.path:
                continue
            target = (p.parent / unquote(url.path)).resolve()
            if not target.is_file():
                errors.append(f"{name}: missing CSS asset: {link}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(pages)} pages, {len(files)} files, all local links and fragments.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
