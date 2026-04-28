#!/usr/bin/env python3
"""fukugyo-hyakka - auto_blog_runner エントリポイント wrapper

役割:
  1) scripts/generate_articles.py の generate_all() を呼び出して Hugo Markdown を再生成
  2) `hugo --quiet` で静的サイトをビルド (sitemap も自動更新)

このサイトは現状テンプレートベースの記事生成 (Gemini API 等の LLM 呼び出しなし) のため、
auto_blog_runner.py から LLM_BACKEND=claude が渡されても無視して問題ない。
"""
from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _generate_articles() -> int:
    """scripts/generate_articles.py の generate_all() を呼ぶ。"""
    sys.path.insert(0, str(SCRIPTS))
    try:
        import generate_articles  # type: ignore
    except ImportError as exc:
        logger.error("scripts/generate_articles.py の import に失敗: %s", exc)
        raise
    count = generate_articles.generate_all()
    logger.info("generated %d articles", count)
    return count


def _hugo_build() -> None:
    """hugo --quiet で静的サイトをビルド。"""
    hugo = shutil.which("hugo")
    if not hugo:
        logger.warning("hugo が PATH に見つからないためビルドをスキップ")
        return
    logger.info("hugo --quiet (cwd=%s)", ROOT)
    proc = subprocess.run(
        [hugo, "--quiet"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )
    if proc.returncode != 0:
        logger.error("hugo build failed (rc=%d): %s", proc.returncode, proc.stderr.strip()[-1000:])
        raise SystemExit(proc.returncode)
    logger.info("hugo build OK")


def main() -> None:
    logger.info("=== fukugyo-hyakka generate_and_build start ===")
    _generate_articles()
    _hugo_build()
    logger.info("=== fukugyo-hyakka generate_and_build done ===")


if __name__ == "__main__":
    main()
