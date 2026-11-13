#!/usr/bin/env python3
"""Static checks for site/: document basics, local refs, and the launch contract.

Usage:
    python3 -I scripts/check_site.py

Checks every HTML file under site/ for a non-empty <html lang>, <title> and
viewport meta, then verifies that local href/src references and CSS url()
resources exist inside site/. Also enforces the site contract: both landing
pages' title/description/canonical/hreflang (including x-default)/WebSite +
SoftwareApplication JSON-LD and FatWhale site brand, the four Chinese topic
pages and their canonicals/topics/internal links/BreadcrumbList JSON-LD,
the FAQ page's FAQPage JSON-LD (answers match visible text), share images
(og:image + Twitter card) on all six pages, site/404.html, robots.txt,
sitemap.xml with a <lastmod> on every URL, the DSH Mobile App brand name,
and no Chinese left in English content outside the zh-CN language switches.
No third-party dependencies.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

SITE_URL = "https://fatwhale.app/"
BRAND = "DSH Mobile App"
FEATURE = "DeepSeek Harness"
BRAND_ALIAS = "FatWhale"
RELEASES_URL = "https://github.com/solla-h/dsh-mobile-app/releases"
EXPECTED_PAGES = {
    "index.html": SITE_URL,
    "en/index.html": "https://fatwhale.app/en/",
}
CONTENT_PAGES = {
    "install/index.html": ("https://fatwhale.app/install/", "安装与配对"),
    "compatibility/index.html": ("https://fatwhale.app/compatibility/", "版本兼容"),
    "faq/index.html": ("https://fatwhale.app/faq/", "常见问题"),
    "download/index.html": ("https://fatwhale.app/download/", "APK 下载"),
}
EXPECTED_HREFLANGS = {
    "zh-cn": SITE_URL,
    "en": "https://fatwhale.app/en/",
}
SITEMAP_URL = "https://fatwhale.app/sitemap.xml"
SITEMAP_LOCS = set(EXPECTED_PAGES.values()) | {
    canonical for canonical, _topic in CONTENT_PAGES.values()
}
FORBIDDEN_SOFTWARE_FIELDS = {"aggregateRating", "review", "softwareVersion", "offers"}
OLD_BRAND_RE = re.compile(r"DSH\s+Mobile(?!\s+App)")
LASTMOD_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
OG_IMAGE = SITE_URL + "og-cover.png"
OG_IMAGE_EN = SITE_URL + "og-cover-en.png"
CJK_RE = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
ROBOTS_SITEMAP_RE = re.compile(r"sitemap:\s*https://fatwhale\.app/sitemap\.xml", re.IGNORECASE)
ROBOTS_DISALLOW_ALL_RE = re.compile(r"disallow:\s*/\s*", re.IGNORECASE)

IGNORED_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript", "ftp"}
URL_ATTRS = {
    ("a", "href"),
    ("link", "href"),
    ("script", "src"),
    ("img", "src"),
    ("img", "data-still"),
    ("img", "data-idle"),
    ("img", "data-happy"),
    ("source", "src"),
    ("video", "poster"),
}
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(?P<ref>[^'\")]+)\1\s*\)", re.IGNORECASE)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.viewport = ""
        self.description = ""
        self.og_site_name = ""
        self.og_image = ""
        self.og_image_width = ""
        self.og_image_height = ""
        self.og_image_alt = ""
        self.twitter_card = ""
        self.twitter_image = ""
        self.text_parts: list[str] = []
        self.noindex = False
        self.canonicals: list[str] = []
        self.hreflangs: list[tuple[str, str]] = []
        self.jsonld: list[str] = []
        self.chinese_leaks: list[str] = []
        self.title_parts: list[str] = []
        self.refs: list[tuple[str, str, str]] = []
        self._in_title = False
        self._in_script = False
        self._in_jsonld = False
        self._jsonld_parts: list[str] = []
        self._zh_anchor: list[bool] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {key.lower(): (value or "") for key, value in attrs}

        if tag == "html":
            self.lang = values.get("lang", "").strip()
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = values.get("name", "").strip().lower()
            prop = values.get("property", "").strip().lower()
            content = values.get("content", "").strip()
            if name == "viewport":
                self.viewport = content
            elif name == "description":
                self.description = content
            elif name in {"robots", "googlebot"}:
                directives = re.split(r"[\s,]+", content.lower())
                self.noindex |= bool({"noindex", "none"}.intersection(directives))
            elif name == "twitter:card":
                self.twitter_card = content
            elif name == "twitter:image":
                self.twitter_image = content
            elif prop == "og:site_name":
                self.og_site_name = content
            elif prop == "og:image":
                self.og_image = content
            elif prop == "og:image:width":
                self.og_image_width = content
            elif prop == "og:image:height":
                self.og_image_height = content
            elif prop == "og:image:alt":
                self.og_image_alt = content
        elif tag == "link":
            rels = values.get("rel", "").lower().split()
            href = values.get("href", "").strip()
            if "canonical" in rels:
                self.canonicals.append(href)
            elif "alternate" in rels and "hreflang" in values:
                self.hreflangs.append((values["hreflang"].strip().lower(), href))
        elif tag == "script":
            self._in_script = True
            if values.get("type", "").strip().lower() == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_parts = []
        elif tag == "a":
            self._zh_anchor.append(values.get("lang", "").strip().lower() == "zh-cn")

        if not self._in_script:
            for key, value in values.items():
                if CJK_RE.search(value) and not (
                    tag == "a" and values.get("lang", "").strip().lower() == "zh-cn"
                ):
                    self.chinese_leaks.append(f"attribute {key}")

        for ref_tag, ref_attr in URL_ATTRS:
            if tag == ref_tag and values.get(ref_attr, "").strip():
                self.refs.append((tag, ref_attr, values[ref_attr].strip()))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "a" and self._zh_anchor:
            self._zh_anchor.pop()
        elif tag == "script":
            if self._in_jsonld:
                self.jsonld.append("".join(self._jsonld_parts))
                self._jsonld_parts = []
                self._in_jsonld = False
            self._in_script = False
        if tag in {"p", "div", "li", "details", "summary"} | {f"h{n}" for n in range(1, 7)}:
            self.text_parts.append(" ")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_jsonld:
            self._jsonld_parts.append(data)
        if self._in_script:
            return
        self.text_parts.append(data)
        if CJK_RE.search(data) and not (self._zh_anchor and self._zh_anchor[-1]):
            self.chinese_leaks.append("text")

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def visible_text(self) -> str:
        """Page text as a reader sees it: tags contribute nothing, block
        boundaries separate, whitespace collapsed."""
        return re.sub(r"\s+", " ", "".join(self.text_parts)).strip()


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


def check_html(path: Path, errors: list[str], counter: list[int]) -> PageParser | None:
    parser = PageParser()
    try:
        text = path.read_text(encoding="utf-8")
        parser.feed(text)
        parser.close()
    except UnicodeDecodeError as exc:
        errors.append(f"{display(path)}: not valid UTF-8 ({exc})")
        return None

    if not parser.lang:
        errors.append(f"{display(path)}: missing non-empty <html lang>")
    if not parser.title:
        errors.append(f"{display(path)}: missing non-empty <title>")
    if not parser.viewport:
        errors.append(f"{display(path)}: missing viewport meta")
    elif "width=device-width" not in parser.viewport.lower():
        errors.append(f"{display(path)}: viewport must include width=device-width")

    if parser.noindex:
        errors.append(f"{display(path)}: noindex prevents production indexing")

    if OLD_BRAND_RE.search(text):
        errors.append(f'{display(path)}: stale brand name, use "{BRAND}"')

    for _tag, _attr, ref in parser.refs:
        check_ref(path, ref, errors, counter)

    return parser


def check_css(path: Path, errors: list[str], counter: list[int]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{display(path)}: not valid UTF-8 ({exc})")
        return

    for match in CSS_URL_RE.finditer(text):
        check_ref(path, match.group("ref"), errors, counter)


def check_website_jsonld(parser: PageParser, label: str, errors: list[str]) -> None:
    if not parser.jsonld:
        errors.append(f"{label}: missing WebSite JSON-LD")
        return

    found = False
    for raw in parser.jsonld:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{label}: invalid JSON-LD ({exc.msg})")
            continue
        for item in data if isinstance(data, list) else [data]:
            if not isinstance(item, dict) or item.get("@type") != "WebSite":
                continue
            found = True
            if item.get("@context") != "https://schema.org":
                errors.append(f'{label}: WebSite JSON-LD @context must be "https://schema.org"')
            if item.get("name") != BRAND:
                errors.append(f'{label}: WebSite JSON-LD name must be "{BRAND}"')
            if item.get("url") != SITE_URL:
                errors.append(f'{label}: WebSite JSON-LD url must be "{SITE_URL}"')

    if not found:
        errors.append(f"{label}: missing WebSite JSON-LD")


def check_software_jsonld(parser: PageParser, label: str, errors: list[str]) -> None:
    software = None
    for raw in parser.jsonld:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue  # already reported by check_website_jsonld
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict) and item.get("@type") == "SoftwareApplication":
                software = item

    if software is None:
        errors.append(f"{label}: missing SoftwareApplication JSON-LD")
        return

    if software.get("@context") != "https://schema.org":
        errors.append(f'{label}: SoftwareApplication @context must be "https://schema.org"')
    if software.get("name") != BRAND:
        errors.append(f'{label}: SoftwareApplication name must be "{BRAND}"')
    if software.get("url") != SITE_URL:
        errors.append(f'{label}: SoftwareApplication url must be "{SITE_URL}"')
    if software.get("operatingSystem") != "Android":
        errors.append(f'{label}: SoftwareApplication operatingSystem must be "Android"')
    if not software.get("applicationCategory"):
        errors.append(f"{label}: SoftwareApplication needs an applicationCategory")
    if software.get("downloadUrl") != RELEASES_URL:
        errors.append(
            f"{label}: SoftwareApplication downloadUrl must be {RELEASES_URL}; "
            "do not pin an APK filename or use /releases/latest"
        )
    for key in sorted(FORBIDDEN_SOFTWARE_FIELDS & software.keys()):
        errors.append(
            f"{label}: SoftwareApplication must not declare {key} "
            "(no invented ratings, reviews or pinned versions)"
        )


def check_brand_positioning(pages: dict[str, PageParser], errors: list[str]) -> None:
    for rel in EXPECTED_PAGES:
        parser = pages.get(rel)
        if parser is None:
            continue
        label = f"site/{rel}"
        if BRAND_ALIAS not in parser.title:
            errors.append(f'{label}: <title> must contain the site brand "{BRAND_ALIAS}"')
        if BRAND_ALIAS not in parser.description:
            errors.append(f'{label}: meta description must contain "{BRAND_ALIAS}"')
        if BRAND_ALIAS not in parser.og_site_name:
            errors.append(f'{label}: og:site_name must contain "{BRAND_ALIAS}"')


def jsonld_items(parser: PageParser) -> list[dict]:
    items: list[dict] = []
    for raw in parser.jsonld:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue  # already reported by check_website_jsonld
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict):
                items.append(item)
    return items


def check_share_images(pages: dict[str, PageParser], errors: list[str]) -> None:
    for rel in list(EXPECTED_PAGES) + list(CONTENT_PAGES):
        parser = pages.get(rel)
        label = f"site/{rel}"
        if parser is None:
            continue
        expected = OG_IMAGE_EN if rel == "en/index.html" else OG_IMAGE
        if parser.og_image != expected:
            errors.append(f"{label}: og:image must be {expected}")
        if parser.og_image_width != "1200" or parser.og_image_height != "630":
            errors.append(f"{label}: og:image must declare 1200x630")
        if not parser.og_image_alt:
            errors.append(f"{label}: og:image needs a non-empty alt")
        if parser.twitter_card != "summary_large_image":
            errors.append(f"{label}: twitter:card must be summary_large_image")
        if parser.twitter_image != expected:
            errors.append(f"{label}: twitter:image must match og:image")


def check_faq_jsonld(pages: dict[str, PageParser], errors: list[str]) -> None:
    parser = pages.get("faq/index.html")
    label = "site/faq/index.html"
    if parser is None:
        errors.append(f"{label}: missing FAQ page")
        return
    faq = None
    for item in jsonld_items(parser):
        if item.get("@type") == "FAQPage":
            faq = item
    if faq is None:
        errors.append(f"{label}: missing FAQPage JSON-LD")
        return
    entities = faq.get("mainEntity")
    if not isinstance(entities, list) or not entities:
        errors.append(f"{label}: FAQPage needs a non-empty mainEntity list")
        return
    visible = parser.visible_text
    for entity in entities:
        if not isinstance(entity, dict) or entity.get("@type") != "Question":
            errors.append(f"{label}: FAQPage mainEntity entries must be Questions")
            continue
        question = entity.get("name", "")
        answer = entity.get("acceptedAnswer", {})
        answer_text = answer.get("text", "") if isinstance(answer, dict) else ""
        norm = lambda s: re.sub(r"\s+", " ", str(s)).strip()
        if not question or norm(question) not in visible:
            errors.append(f"{label}: FAQPage question not found in visible text: {question!r}")
        if not answer_text or norm(answer_text) not in visible:
            errors.append(f"{label}: FAQPage answer not found in visible text: {question!r}")


def check_breadcrumb_jsonld(pages: dict[str, PageParser], errors: list[str]) -> None:
    for rel, (canonical, topic) in CONTENT_PAGES.items():
        parser = pages.get(rel)
        label = f"site/{rel}"
        if parser is None:
            continue
        crumbs = None
        for item in jsonld_items(parser):
            if item.get("@type") == "BreadcrumbList":
                crumbs = item
        if crumbs is None:
            errors.append(f"{label}: missing BreadcrumbList JSON-LD")
            continue
        elements = crumbs.get("itemListElement")
        if not isinstance(elements, list) or len(elements) != 2:
            errors.append(f"{label}: BreadcrumbList needs exactly two items (home, this page)")
            continue
        first, second = elements
        if not isinstance(first, dict) or first.get("item") != SITE_URL:
            errors.append(f"{label}: BreadcrumbList first item must be {SITE_URL}")
        if not isinstance(second, dict) or second.get("item") != canonical:
            errors.append(f"{label}: BreadcrumbList second item must be {canonical}")
        if not isinstance(second, dict) or not str(second.get("name", "")).strip():
            errors.append(f"{label}: BreadcrumbList second item needs a name")


def check_404(pages: dict[str, PageParser], errors: list[str]) -> None:
    parser = pages.get("404.html")
    if parser is None:
        errors.append("site/404.html is missing (unknown paths must return 404, not the homepage)")
        return
    if "404" not in parser.title and "找不到" not in parser.title:
        errors.append("site/404.html: <title> must say the page was not found")


def check_content_pages(pages: dict[str, PageParser], errors: list[str]) -> None:
    for rel, (canonical, topic) in CONTENT_PAGES.items():
        parser = pages.get(rel)
        label = f"site/{rel}"
        if parser is None:
            errors.append(f"{label}: missing content page")
            continue
        if parser.canonicals != [canonical]:
            errors.append(f"{label}: canonical must be exactly {canonical}")
        if BRAND not in parser.title:
            errors.append(f'{label}: <title> must contain "{BRAND}"')
        if topic not in parser.title:
            errors.append(f'{label}: <title> must target its topic "{topic}"')
        if BRAND_ALIAS not in parser.title:
            errors.append(f'{label}: <title> must contain the site brand "{BRAND_ALIAS}"')
        if not parser.description:
            errors.append(f"{label}: missing non-empty meta description")
        internal = [
            ref for tag, _attr, ref in parser.refs
            if tag == "a" and is_local_ref(ref)
        ]
        if len(internal) < 2:
            errors.append(f"{label}: needs at least two internal page links (orphan page)")


def check_bilingual(pages: dict[str, PageParser], errors: list[str]) -> None:
    for rel, canonical in EXPECTED_PAGES.items():
        parser = pages.get(rel)
        label = f"site/{rel}"
        if parser is None:
            errors.append(f"{label}: missing page")
            continue

        if parser.canonicals != [canonical]:
            errors.append(f"{label}: canonical must be exactly {canonical}")
        if BRAND not in parser.title:
            errors.append(f'{label}: <title> must contain "{BRAND}"')
        if FEATURE not in parser.title:
            errors.append(f'{label}: <title> must contain "{FEATURE}"')
        if not parser.description:
            errors.append(f"{label}: missing non-empty meta description")

        hreflangs = dict(parser.hreflangs)
        for lang, href in EXPECTED_HREFLANGS.items():
            if hreflangs.get(lang) != href:
                errors.append(f"{label}: hreflang {lang} must point to {href}")
        if hreflangs.get("x-default") != SITE_URL:
            errors.append(f"{label}: hreflang x-default must point to {SITE_URL}")

        check_website_jsonld(parser, label, errors)
        check_software_jsonld(parser, label, errors)

    english = pages.get("en/index.html")
    if english is not None and english.chinese_leaks:
        kinds = ", ".join(sorted(set(english.chinese_leaks)))
        errors.append(
            "site/en/index.html: Chinese content outside the lang=zh-CN "
            f'language switches ({kinds})'
        )


def check_sitemap(errors: list[str]) -> None:
    path = SITE / "sitemap.xml"
    if not path.is_file():
        errors.append("site/sitemap.xml is missing")
        return

    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, UnicodeDecodeError) as exc:
        errors.append(f"site/sitemap.xml: not valid XML ({exc})")
        return

    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    if root.tag != namespace + "urlset":
        errors.append("site/sitemap.xml: expected sitemap urlset namespace")
    locs = [(element.text or "").strip() for element in root.findall(f"{namespace}url/{namespace}loc")]
    if len(locs) != len(SITEMAP_LOCS) or set(locs) != SITEMAP_LOCS:
        expected = " and ".join(sorted(SITEMAP_LOCS))
        errors.append(f"site/sitemap.xml: must list exactly these URLs: {expected}")
    for element in root.findall(f"{namespace}url"):
        loc = (element.findtext(f"{namespace}loc") or "").strip()
        lastmod = (element.findtext(f"{namespace}lastmod") or "").strip()
        if not LASTMOD_RE.match(lastmod):
            errors.append(f"site/sitemap.xml: {loc or 'a URL'} needs a <lastmod> date (YYYY-MM-DD)")
            continue
        try:
            datetime.strptime(lastmod, "%Y-%m-%d")
        except ValueError:
            errors.append(f"site/sitemap.xml: {loc} has an invalid <lastmod> date: {lastmod}")


def check_robots(errors: list[str]) -> None:
    path = SITE / "robots.txt"
    if not path.is_file():
        errors.append("site/robots.txt is missing")
        return

    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    except UnicodeDecodeError as exc:
        errors.append(f"site/robots.txt: not valid UTF-8 ({exc})")
        return

    if not any(ROBOTS_SITEMAP_RE.fullmatch(line) for line in lines):
        errors.append(f"site/robots.txt: missing Sitemap: {SITEMAP_URL}")
    if any(ROBOTS_DISALLOW_ALL_RE.fullmatch(line) for line in lines):
        errors.append("site/robots.txt: Disallow: / blocks the whole site")


def main() -> int:
    if not SITE.is_dir():
        print(f"FAIL: missing site directory: {display(SITE)}")
        return 1

    html_files = sorted(SITE.rglob("*.html"))
    css_files = sorted(SITE.rglob("*.css"))
    errors: list[str] = []
    counter = [0]
    pages: dict[str, PageParser] = {}

    if not (SITE / "index.html").is_file():
        errors.append("site/index.html is missing")
    if not html_files:
        errors.append("site/ contains no HTML files")

    for path in html_files:
        parser = check_html(path, errors, counter)
        if parser is not None:
            pages[path.relative_to(SITE).as_posix()] = parser
    for path in css_files:
        check_css(path, errors, counter)

    check_bilingual(pages, errors)
    check_brand_positioning(pages, errors)
    check_content_pages(pages, errors)
    check_share_images(pages, errors)
    check_faq_jsonld(pages, errors)
    check_breadcrumb_jsonld(pages, errors)
    check_404(pages, errors)
    check_sitemap(errors)
    check_robots(errors)

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
