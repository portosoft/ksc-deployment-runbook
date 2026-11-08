#!/usr/bin/env python3
import argparse
import hashlib
import os
import re
import shutil
import sys
import tarfile
from pathlib import Path

def extract_changelog_notes(version, changelog_path):
    version = version.lstrip('v')
    content = changelog_path.read_text(encoding='utf-8')
    # The changelog format uses em dash (—) or similar: ## [2.0.0] — 2026-09-13
    pattern = rf"## \[{version}\] [—-] \d{{4}}-\d{{2}}-\d{{2}}\n+(.*?)\n+(?=## \[[0-9]|## \[Unreleased\])"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()

    pattern_last = rf"## \[{version}\] [—-] \d{{4}}-\d{{2}}-\d{{2}}\n+(.*)"
    match_last = re.search(pattern_last, content, re.DOTALL)
    if match_last:
        return match_last.group(1).strip()
    return ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tar_name = f"ksc-deployment-runbook-{args.version}.tar.gz"
    tar_path = out_dir / tar_name

    excludes = ['.git', '__pycache__', '.secrets.baseline', 'tests', 'evidence', '.venv', '.jules', '.kiro', '.agents', 'scripts', 'docs/internal']

    with tarfile.open(tar_path, "w:gz") as tar:
        for item in repo_root.iterdir():
            if any(item.name == ex or str(item.relative_to(repo_root)).startswith(ex) for ex in excludes):
                continue
            if item.name == tar_name:
                 continue
            tar.add(item, arcname=item.name, filter=lambda ti: None if any(ex in ti.name for ex in excludes) else ti)

    sha256 = hashlib.sha256(tar_path.read_bytes()).hexdigest()
    sums_file = out_dir / "SHA256SUMS"
    sums_file.write_text(f"{sha256}  {tar_name}\n")

if __name__ == '__main__':
    main()
