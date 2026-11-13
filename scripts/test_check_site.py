#!/usr/bin/env python3
"""Regression checks for scripts/check_site.py against the site contract.

Usage:
    python3 -I scripts/test_check_site.py

Builds a minimal site/ fixture in a temp directory, copies check_site.py next
to it and runs that copy as a subprocess. Asserts the valid fixture passes and
that broken canonicals, JSON-LD, sitemap entries, topic pages, SoftwareApplication
data, brand positioning, share images, hreflang x-default, FAQPage answers,
BreadcrumbList targets, sitemap lastmod, the 404 page and Chinese left in
English content are rejected.
Standard library only, no third-party deps.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECK_SITE = Path(__file__).resolve().parent / "check_site.py"

WEBSITE_JSONLD = '{"@context": "https://schema.org", "@type": "WebSite", "name": "DSH Mobile App", "url": "https://fatwhale.app/"}'
SOFTWARE_JSONLD = (
    '{"@context": "https://schema.org", "@type": "SoftwareApplication", '
    '"name": "DSH Mobile App", "url": "https://fatwhale.app/", '
    '"applicationCategory": "DeveloperApplication", "operatingSystem": "Android", '
    '"downloadUrl": "https://github.com/solla-h/dsh-mobile-app/releases"}'
)
RELEASES_FIELD = '"downloadUrl": "https://github.com/solla-h/dsh-mobile-app/releases"'

ZH_PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>大肥鱼 FatWhale · DSH Mobile App — DeepSeek Harness 第三方 Android 客户端</title>
  <meta name="description" content="大肥鱼 FatWhale 官网。DSH Mobile App 是配套 DeepSeek Harness 的第三方 Android 客户端。">
  <meta property="og:site_name" content="大肥鱼 FatWhale · DSH Mobile App">
  <meta property="og:image" content="https://fatwhale.app/og-cover.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="大肥鱼 FatWhale · DSH Mobile App">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://fatwhale.app/og-cover.png">
  <link rel="canonical" href="https://fatwhale.app/">
  <link rel="alternate" hreflang="zh-CN" href="https://fatwhale.app/">
  <link rel="alternate" hreflang="en" href="https://fatwhale.app/en/">
  <link rel="alternate" hreflang="x-default" href="https://fatwhale.app/">
  <script type="application/ld+json">WEBSITE_JSONLD</script>
  <script type="application/ld+json">SOFTWARE_JSONLD</script>
</head>
<body><a href="en/" hreflang="en" lang="en">English</a></body>
</html>
""".replace("WEBSITE_JSONLD", WEBSITE_JSONLD).replace("SOFTWARE_JSONLD", SOFTWARE_JSONLD)

EN_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FatWhale · DSH Mobile App — Android Client for DeepSeek Harness</title>
  <meta name="description" content="FatWhale is the site brand for DSH Mobile App, an open-source Android client for DeepSeek Harness.">
  <meta property="og:site_name" content="FatWhale · DSH Mobile App">
  <meta property="og:image" content="https://fatwhale.app/og-cover-en.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="FatWhale · DSH Mobile App">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://fatwhale.app/og-cover-en.png">
  <link rel="canonical" href="https://fatwhale.app/en/">
  <link rel="alternate" hreflang="zh-CN" href="https://fatwhale.app/">
  <link rel="alternate" hreflang="en" href="https://fatwhale.app/en/">
  <link rel="alternate" hreflang="x-default" href="https://fatwhale.app/">
  <script type="application/ld+json">WEBSITE_JSONLD</script>
  <script type="application/ld+json">SOFTWARE_JSONLD</script>
</head>
<body>
  <header><a href="../" hreflang="zh-CN" lang="zh-CN">中文</a></header>
  <main><p>Check progress. Handle approvals.</p></main>
  <footer><a href="../" hreflang="zh-CN" lang="zh-CN">简体中文</a></footer>
</body>
</html>
""".replace("WEBSITE_JSONLD", WEBSITE_JSONLD).replace("SOFTWARE_JSONLD", SOFTWARE_JSONLD)

CONTENT_PAGES = {
    "install/index.html": ("https://fatwhale.app/install/", "安装与配对"),
    "compatibility/index.html": ("https://fatwhale.app/compatibility/", "版本兼容"),
    "faq/index.html": ("https://fatwhale.app/faq/", "常见问题"),
    "download/index.html": ("https://fatwhale.app/download/", "APK 下载"),
}


OG_CN = """  <meta property="og:image" content="https://fatwhale.app/og-cover.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="大肥鱼 FatWhale · DSH Mobile App">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://fatwhale.app/og-cover.png">"""

FAQ_JSONLD = '{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "这是 DeepSeek 官方的 App 吗？", "acceptedAnswer": {"@type": "Answer", "text": "不是。DSH Mobile App 是独立的第三方开源项目。"}}]}'


def content_page(canonical: str, topic: str) -> str:
    breadcrumb = (
        '{"@context": "https://schema.org", "@type": "BreadcrumbList", '
        '"itemListElement": [{"@type": "ListItem", "position": 1, "name": "首页", '
        '"item": "https://fatwhale.app/"}, {"@type": "ListItem", "position": 2, '
        f'"name": "{topic}", "item": "{canonical}"}}]}}'
    )
    faq_block = ""
    faq_body = ""
    if canonical == "https://fatwhale.app/faq/":
        faq_block = f'\n  <script type="application/ld+json">{FAQ_JSONLD}</script>'
        faq_body = (
            "\n  <details><summary>这是 DeepSeek 官方的 App 吗？</summary>"
            '<div class="answer"><p>不是。DSH Mobile App 是独立的第三方开源项目。</p></div></details>'
        )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DSH Mobile App {topic}｜大肥鱼 FatWhale</title>
  <meta name="description" content="大肥鱼 FatWhale 官网：DSH Mobile App {topic} 专题页。">
  <link rel="canonical" href="{canonical}">
{OG_CN}
  <script type="application/ld+json">{breadcrumb}</script>{faq_block}
</head>
<body>
  <a href="../">首页</a>
  <a href="../faq/">常见问题</a>{faq_body}
</body>
</html>
"""


NOT_FOUND = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>找不到这个页面 · 大肥鱼 FatWhale</title>
</head>
<body><p>这个页面不存在。</p></body>
</html>
"""

ROBOTS = "User-agent: *\nAllow: /\nSitemap: https://fatwhale.app/sitemap.xml\n"

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://fatwhale.app/</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://fatwhale.app/en/</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://fatwhale.app/install/</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://fatwhale.app/compatibility/</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://fatwhale.app/faq/</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://fatwhale.app/download/</loc><lastmod>2026-11-13</lastmod></url>
</urlset>
"""

JSONLD = WEBSITE_JSONLD


def write_fixture(root: Path) -> None:
    site = root / "site"
    (site / "en").mkdir(parents=True)
    (site / "index.html").write_text(ZH_PAGE, encoding="utf-8")
    (site / "en" / "index.html").write_text(EN_PAGE, encoding="utf-8")
    for rel, (canonical, topic) in CONTENT_PAGES.items():
        path = site / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content_page(canonical, topic), encoding="utf-8")
    (site / "404.html").write_text(NOT_FOUND, encoding="utf-8")
    (site / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    (site / "sitemap.xml").write_text(SITEMAP, encoding="utf-8")


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"fixture text not found: {old}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def run_checker(mutate=None) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        scripts = root / "scripts"
        scripts.mkdir()
        shutil.copyfile(CHECK_SITE, scripts / "check_site.py")
        write_fixture(root)
        if mutate is not None:
            mutate(root / "site")
        return subprocess.run(
            [sys.executable, "-I", str(scripts / "check_site.py")],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
        )


def test_valid_fixture_passes() -> None:
    result = run_checker()
    assert result.returncode == 0, result.stdout + result.stderr


def test_wrong_canonical_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "en" / "index.html",
            '<link rel="canonical" href="https://fatwhale.app/en/">',
            '<link rel="canonical" href="https://fatwhale.app/">',
        )

    result = run_checker(mutate)
    assert result.returncode != 0
    assert "canonical" in result.stdout, result.stdout


def test_broken_jsonld_fails() -> None:
    def mutate(site: Path) -> None:
        replace(site / "en" / "index.html", JSONLD, '{"@context": "https://schema.org"')

    result = run_checker(mutate)
    assert result.returncode != 0
    assert "JSON-LD" in result.stdout, result.stdout


def test_missing_sitemap_url_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "sitemap.xml",
            "<url><loc>https://fatwhale.app/en/</loc><lastmod>2026-11-13</lastmod></url>\n",
            "",
        )

    result = run_checker(mutate)
    assert result.returncode != 0
    assert "sitemap" in result.stdout.lower(), result.stdout


def test_chinese_in_english_page_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "en" / "index.html",
            "<main><p>Check progress. Handle approvals.</p></main>",
            '<main><p lang="zh-CN">家里的工作站</p></main>',
        )

    result = run_checker(mutate)
    assert result.returncode != 0
    assert "Chinese" in result.stdout, result.stdout


def test_noindex_fails() -> None:
    def mutate(site: Path) -> None:
        replace(site / "index.html", "</head>", '<meta name="robots" content="noindex"></head>')

    result = run_checker(mutate)
    assert result.returncode != 0 and "noindex" in result.stdout, result.stdout


def test_missing_pet_animation_fails() -> None:
    def mutate(site: Path) -> None:
        replace(site / "index.html", "</body>", '<img alt="" data-idle="missing-pet.webp"></body>')

    result = run_checker(mutate)
    assert result.returncode != 0 and "missing-pet.webp" in result.stdout, result.stdout


def test_missing_software_jsonld_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "index.html",
            f'  <script type="application/ld+json">{SOFTWARE_JSONLD}</script>\n',
            "",
        )

    result = run_checker(mutate)
    assert result.returncode != 0 and "SoftwareApplication" in result.stdout, result.stdout


def test_bad_download_url_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "index.html",
            RELEASES_FIELD,
            RELEASES_FIELD.replace('releases"', 'releases/latest"'),
        )

    result = run_checker(mutate)
    assert result.returncode != 0 and "downloadUrl" in result.stdout, result.stdout


def test_invented_rating_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "en" / "index.html",
            '"@type": "SoftwareApplication",',
            '"@type": "SoftwareApplication", "aggregateRating": {"@type": "AggregateRating"},',
        )

    result = run_checker(mutate)
    assert result.returncode != 0 and "aggregateRating" in result.stdout, result.stdout


def test_missing_brand_alias_fails() -> None:
    def mutate(site: Path) -> None:
        replace(site / "index.html", "<title>大肥鱼 FatWhale · ", "<title>")

    result = run_checker(mutate)
    assert result.returncode != 0 and "FatWhale" in result.stdout, result.stdout


def test_content_page_wrong_canonical_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "install" / "index.html",
            '<link rel="canonical" href="https://fatwhale.app/install/">',
            '<link rel="canonical" href="https://fatwhale.app/">',
        )

    result = run_checker(mutate)
    assert result.returncode != 0 and "canonical" in result.stdout, result.stdout


def test_content_page_missing_topic_fails() -> None:
    def mutate(site: Path) -> None:
        replace(site / "install" / "index.html", "DSH Mobile App 安装与配对｜", "DSH Mobile App 专题｜")

    result = run_checker(mutate)
    assert result.returncode != 0 and "topic" in result.stdout, result.stdout


def test_orphan_content_page_fails() -> None:
    def mutate(site: Path) -> None:
        replace(site / "install" / "index.html", '  <a href="../faq/">常见问题</a>\n', "")

    result = run_checker(mutate)
    assert result.returncode != 0 and "internal" in result.stdout, result.stdout


def test_missing_og_image_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "index.html",
            '  <meta property="og:image" content="https://fatwhale.app/og-cover.png">\n',
            "",
        )

    result = run_checker(mutate)
    assert result.returncode != 0 and "og:image" in result.stdout, result.stdout


def test_missing_x_default_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "index.html",
            '  <link rel="alternate" hreflang="x-default" href="https://fatwhale.app/">\n',
            "",
        )

    result = run_checker(mutate)
    assert result.returncode != 0 and "x-default" in result.stdout, result.stdout


def test_sitemap_missing_lastmod_fails() -> None:
    def mutate(site: Path) -> None:
        replace(site / "sitemap.xml", "<lastmod>2026-11-13</lastmod>", "")

    result = run_checker(mutate)
    assert result.returncode != 0 and "lastmod" in result.stdout, result.stdout


def test_missing_404_fails() -> None:
    def mutate(site: Path) -> None:
        (site / "404.html").unlink()

    result = run_checker(mutate)
    assert result.returncode != 0 and "404.html" in result.stdout, result.stdout


def test_faq_answer_mismatch_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "faq" / "index.html",
            "不是。DSH Mobile App 是独立的第三方开源项目。",
            "这是一个编造的答案。",
        )

    result = run_checker(mutate)
    assert result.returncode != 0 and "FAQPage" in result.stdout, result.stdout


def test_breadcrumb_wrong_target_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "install" / "index.html",
            '"item": "https://fatwhale.app/install/"',
            '"item": "https://fatwhale.app/"',
        )

    result = run_checker(mutate)
    assert result.returncode != 0 and "BreadcrumbList" in result.stdout, result.stdout


def test_sitemap_missing_content_page_fails() -> None:
    def mutate(site: Path) -> None:
        replace(
            site / "sitemap.xml",
            "<url><loc>https://fatwhale.app/faq/</loc><lastmod>2026-11-13</lastmod></url>\n",
            "",
        )

    result = run_checker(mutate)
    assert result.returncode != 0 and "sitemap" in result.stdout.lower(), result.stdout


def main() -> int:
    tests = (
        test_valid_fixture_passes,
        test_noindex_fails,
        test_wrong_canonical_fails,
        test_broken_jsonld_fails,
        test_missing_sitemap_url_fails,
        test_chinese_in_english_page_fails,
        test_missing_pet_animation_fails,
        test_missing_software_jsonld_fails,
        test_bad_download_url_fails,
        test_invented_rating_fails,
        test_missing_brand_alias_fails,
        test_content_page_wrong_canonical_fails,
        test_content_page_missing_topic_fails,
        test_orphan_content_page_fails,
        test_sitemap_missing_content_page_fails,
        test_missing_og_image_fails,
        test_missing_x_default_fails,
        test_sitemap_missing_lastmod_fails,
        test_missing_404_fails,
        test_faq_answer_mismatch_fails,
        test_breadcrumb_wrong_target_fails,
    )
    for test in tests:
        test()
        print(f"ok: {test.__name__}")

    print(f"OK: {len(tests)} check_site.py regression case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
