#!/usr/bin/env python3
"""Static checks for site/: document basics and local links/resources.

Usage:
    python3 -I scripts/check_site.py

Checks every HTML file under site/ for a non-empty <html lang>, <title> and
viewport meta, then verifies that local href/src references and CSS url()
resources exist inside site/. No third-party dependencies.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

IGNORED_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript", "ftp"}
URL_ATTRS = {
    ("a", "href"),
    ("link", "href"),
    ("script", "src"),
    ("img", "src"),
    ("source", "src"),
    ("video", "poster"),
}
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(?P<ref>[^'\")]+)\1\s*\)", re.IGNORECASE)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.viewport = ""
        self.title_parts: list[str] = []
        self.refs: list[tuple[str, str, str]] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {key.lower(): (value or "") for key, value in attrs}

        if tag == "html":
            self.lang = values.get("lang", "").strip()
        elif tag == "title":
            self._in_title = True
        elif tag == "meta" and values.get("name", "").lower() == "viewport":
            self.viewport = values.get("content", "").strip()

        for ref_tag, ref_attr in URL_ATTRS:
            if tag == ref_tag and values.get(ref_attr, "").strip():
                self.refs.append((tag, ref_attr, values[ref_attr].strip()))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def is_local_ref(ref: str) -> bool:
    ref = ref.strip()
    if not ref or ref.startswith("#") or ref.startswith("//"):
        return False
    return urlsplit(ref).scheme.lower() not in IGNORED_SCHEMES


def resolve_local(base_dir: Path, ref: str) -> tuple[Path, bool] | None:
    """Resolve a local reference; return (target, escapes_site) or None."""
    path = unquote(urlsplit(ref).path)
    if not path:
        return None

    raw = SITE / path.lstrip("/") if path.startswith("/") else base_dir / path
    target = raw.resolve()
    escapes_site = target != SITE and SITE not in target.parents
    if not escapes_site and target.is_dir():
        target = target / "index.html"
    return target, escapes_site


def display(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def check_ref(
    source: Path,
    ref: str,
    errors: list[str],
    counter: list[int],
) -> None:
    if not is_local_ref(ref):
        return

    resolved = resolve_local(source.parent, ref)
    if resolved is None:
        return

    counter[0] += 1
    target, escapes_site = resolved
    if escapes_site:
        errors.append(f"{display(source)}: reference escapes site/: {ref}")
    elif not target.is_file():
        errors.append(f"{display(source)}: missing local target: {ref} -> {display(target)}")


def check_html(path: Path, errors: list[str], counter: list[int]) -> None:
    parser = PageParser()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
        parser.close()
    except UnicodeDecodeError as exc:
        errors.append(f"{display(path)}: not valid UTF-8 ({exc})")
        return

    if not parser.lang:
        errors.append(f"{display(path)}: missing non-empty <html lang>")
    if not parser.title:
        errors.append(f"{display(path)}: missing non-empty <title>")
    if not parser.viewport:
        errors.append(f"{display(path)}: missing viewport meta")
    elif "width=device-width" not in parser.viewport.lower():
        errors.append(f"{display(path)}: viewport must include width=device-width")

    for _tag, _attr, ref in parser.refs:
        check_ref(path, ref, errors, counter)


def check_css(path: Path, errors: list[str], counter: list[int]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{display(path)}: not valid UTF-8 ({exc})")
        return

    for match in CSS_URL_RE.finditer(text):
        check_ref(path, match.group("ref"), errors, counter)


def main() -> int:
    if not SITE.is_dir():
        print(f"FAIL: missing site directory: {display(SITE)}")
        return 1

    html_files = sorted(SITE.rglob("*.html"))
    css_files = sorted(SITE.rglob("*.css"))
    errors: list[str] = []
    counter = [0]

    if not (SITE / "index.html").is_file():
        errors.append("site/index.html is missing")
    if not html_files:
        errors.append("site/ contains no HTML files")

    for path in html_files:
        check_html(path, errors, counter)
    for path in css_files:
        check_css(path, errors, counter)

    for error in errors:
        print(f"ERROR: {error}")

    print(
        f"checked {len(html_files)} HTML file(s), {len(css_files)} CSS file(s), "
        f"{counter[0]} local reference(s)"
    )
    if errors:
        print(f"FAIL: {len(errors)} issue(s)")
        return 1

    print("OK: site checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
