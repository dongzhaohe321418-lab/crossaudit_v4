"""Fragment scan for the wrap-join slice: no run of five or more words from any file
under the archive may appear in a file this slice commits.

    python benchmarks/expertlongbench/study15/wrapjoin_scan.py --run <archive>/arm6 \
        [--baseline <dir-or-file> ...] <file>...

Every text file under the archive (the projects' drafts, sources, ledgers, receipts, the
run log and records) is shingled into runs of 5 lower-cased word tokens; the repo's own
`contract-S.txt`, `skill-S.md` and `plan*.json` are excluded because they are the product's
text, not the corpus. `--baseline` names the repo's own committed text (the product, the
harness, the earlier records — nothing in it is corpus text by the repo's rule), whose
shingles are subtracted from the archive's: what remains is what only the archive says —
the rendered skill under each project's `skills/`, the harness's path names and the fence
keys in every draft are the product's vocabulary and not the corpus's. Each committed file
is shingled the same way; every shingle it shares with the remaining archive set is
reported as a shape (file, line number, the count of shared runs) — never as the words.
Exit 1 on any hit.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-]*")
N = 5
EXCLUDED = {"contract-S.txt", "skill-S.md"}


def shingles(text: str) -> set[tuple[str, ...]]:
    words = [w.lower() for w in WORD.findall(text)]
    return {tuple(words[i:i + N]) for i in range(len(words) - N + 1)}


def _text_files(root: Path):
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts and ".venv" not in path.parts:
            yield path


def archive_shingles(run_dir: Path) -> set[tuple[str, ...]]:
    out: set[tuple[str, ...]] = set()
    for path in _text_files(run_dir):
        if path.name in EXCLUDED or path.name.startswith("plan"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        out |= shingles(text)
    return out


def baseline_shingles(roots: list[str]) -> set[tuple[str, ...]]:
    out: set[tuple[str, ...]] = set()
    for root in roots:
        for path in _text_files(Path(root)):
            try:
                out |= shingles(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, OSError):
                continue
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--baseline", action="append", default=[])
    ap.add_argument("files", nargs="+")
    args = ap.parse_args(argv)
    corpus = archive_shingles(Path(args.run))
    print(f"archive shingles ({N} words): {len(corpus)}")
    if args.baseline:
        base = baseline_shingles(args.baseline)
        corpus -= base
        print(f"baseline shingles {len(base)}; archive-only shingles {len(corpus)}")
    hits = 0
    for name in args.files:
        text = Path(name).read_text(encoding="utf-8")
        for no, line in enumerate(text.split("\n"), 1):
            shared = shingles(line) & corpus
            if shared:
                hits += len(shared)
                print(f"HIT {name}:{no}: {len(shared)} shared {N}-word run(s)")
    print(f"{'FAIL' if hits else 'clean'}: {hits} shared run(s) over {len(args.files)} file(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
