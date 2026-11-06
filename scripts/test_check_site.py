#!/usr/bin/env python3
"""Regression checks for scripts/check_site.py against the bilingual contract.

Usage:
    python3 -I scripts/test_check_site.py

Builds a minimal site/ fixture in a temp directory, copies check_site.py next
to it and runs that copy as a subprocess. Asserts the valid fixture passes and
that a wrong canonical, broken JSON-LD, a missing sitemap URL and Chinese left
in English content are rejected. Standard library only, no third-party deps.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECK_SITE = Path(__file__).resolve().parent / "check_site.py"

ZH_PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DSH Mobile App — DeepSeek Harness 第三方 Android 客户端</title>
  <meta name="description" content="DSH Mobile App 是配套 DeepSeek Harness 的第三方 Android 客户端。">
  <link rel="canonical" href="https://fatwhale.app/">
  <link rel="alternate" hreflang="zh-CN" href="https://fatwhale.app/">
  <link rel="alternate" hreflang="en" href="https://fatwhale.app/en/">
  <script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebSite", "name": "DSH Mobile App", "url": "https://fatwhale.app/"}</script>
</head>
<body><a href="en/" hreflang="en" lang="en">English</a></body>
</html>
"""

EN_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DSH Mobile App — Android Client for DeepSeek Harness</title>
  <meta name="description" content="DSH Mobile App is an open-source Android client for DeepSeek Harness.">
  <link rel="canonical" href="https://fatwhale.app/en/">
  <link rel="alternate" hreflang="zh-CN" href="https://fatwhale.app/">
  <link rel="alternate" hreflang="en" href="https://fatwhale.app/en/">
  <script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebSite", "name": "DSH Mobile App", "url": "https://fatwhale.app/"}</script>
</head>
<body>
  <header><a href="../" hreflang="zh-CN" lang="zh-CN">中文</a></header>
  <main><p>Check progress. Handle approvals.</p></main>
  <footer><a href="../" hreflang="zh-CN" lang="zh-CN">简体中文</a></footer>
</body>
</html>
"""

ROBOTS = "User-agent: *\nAllow: /\nSitemap: https://fatwhale.app/sitemap.xml\n"

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://fatwhale.app/</loc></url>
  <url><loc>https://fatwhale.app/en/</loc></url>
</urlset>
"""

JSONLD = '{"@context": "https://schema.org", "@type": "WebSite", "name": "DSH Mobile App", "url": "https://fatwhale.app/"}'


def write_fixture(root: Path) -> None:
    site = root / "site"
    (site / "en").mkdir(parents=True)
    (site / "index.html").write_text(ZH_PAGE, encoding="utf-8")
    (site / "en" / "index.html").write_text(EN_PAGE, encoding="utf-8")
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
        replace(site / "sitemap.xml", "<url><loc>https://fatwhale.app/en/</loc></url>\n", "")

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


def main() -> int:
    tests = (
        test_valid_fixture_passes,
        test_noindex_fails,
        test_wrong_canonical_fails,
        test_broken_jsonld_fails,
        test_missing_sitemap_url_fails,
        test_chinese_in_english_page_fails,
        test_missing_pet_animation_fails,
    )
    for test in tests:
        test()
        print(f"ok: {test.__name__}")

    print(f"OK: {len(tests)} check_site.py regression case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
