#!/usr/bin/env python3
"""
setup_nltk_prj381.py
--------------------
Run once after you've `pip install nltk` (inside your venv).

• Downloads the resources your scorer needs:   punkt  +  averaged_perceptron_tagger
• Then duplicates tokenizers/punkt → tokenizers/punkt_tab
  so every NLTK build can locate the files.

Usage:
    $ python setup_nltk_prj381.py
"""

import os
import shutil
from pathlib import Path
import nltk

RESOURCES = ["punkt", "averaged_perceptron_tagger"]


def _target_dir() -> Path:
    """Choose where to put the data (same order NLTK searches)."""
    if os.getenv("NLTK_DATA"):
        return Path(os.getenv("NLTK_DATA")).expanduser()
    if os.getenv("VIRTUAL_ENV"):
        return Path(os.getenv("VIRTUAL_ENV")) / "nltk_data"
    return Path.home() / "nltk_data"


def main() -> None:
    target = _target_dir()
    target.mkdir(parents=True, exist_ok=True)

    print(f"\n📥  Downloading {', '.join(RESOURCES)} into {target} …")
    for res in RESOURCES:
        nltk.download(res, download_dir=str(target), quiet=False)

    # ---- punkt → punkt_tab shim ------------------------------------------
    src = target / "tokenizers" / "punkt"
    dst = target / "tokenizers" / "punkt_tab"
    if src.exists() and not dst.exists():
        print(f"🔗  Creating fallback dir {dst}")
        shutil.copytree(src, dst)

    print("\n✅  NLTK data ready.  You shouldn’t see the 'punkt_tab not found' error again.")


if __name__ == "__main__":
    main()
