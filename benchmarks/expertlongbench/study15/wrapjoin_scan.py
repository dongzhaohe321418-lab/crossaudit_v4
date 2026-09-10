"""Fragment scan for the wrap-join slice: no run of five or more words from any file
under the archive may appear in a file this slice commits.

    python benchmarks/expertlongbench/study15/wrapjoin_scan.py --run <archive>/arm6 \
        --baseline-rev 1f6120e [--baseline-path src ...] <file>...

Every text file under the archive (the projects' drafts, sources, ledgers, receipts, the
run log and records) is shingled as ONE text — newlines folded to spaces, so a run that
crosses a line break is a run — into runs of 5 lower-cased word tokens; the repo's own
`contract-S.txt`, `skill-S.md` and `plan*.json` are excluded because they are the product's
text, not the corpus. `--baseline-rev` names the commit BEFORE this slice (1f6120e, the
branch point), and the baseline is read from that commit with `git show <rev>:<path>` for
every file under the `--baseline-path`s (default `src`, `benchmarks/expertlongbench`,
`docs`): the product, the harness and the earlier records hold no corpus text by the
repo's rule, and taking the baseline from a commit that predates the candidate files means
no candidate can launder its own shingles through the subtraction. What remains is what
only the archive says. Each candidate file is shingled the same way, as one text; every
shingle it shares with the remaining archive set is reported as a shape (file, the line
where the run starts, the count) — never as the words. Exit 1 on any hit.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

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


def baseline_shingles(repo: Path, rev: str, paths: list[str]) -> set[tuple[str, ...]]:
    """The shingles of every file under `paths` as committed at `rev`, read with
    `git show` so the working tree — the candidates included — plays no part."""
    listing = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev, "--", *paths],
                             cwd=str(repo), capture_output=True, text=True, check=True).stdout
    out: set[tuple[str, ...]] = set()
    for rel in listing.split("\n"):
        if not rel.strip():
            continue
        blob = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=str(repo),
                              capture_output=True, check=True).stdout
        try:
            out |= shingles(blob.decode("utf-8"))
        except UnicodeDecodeError:
            continue
    return out


def shared_runs(text: str, corpus: set[tuple[str, ...]]) -> list[int]:
    """The line number (1-based) at which every shared run starts, over the whole text."""
    tokens = [(m.group(0).lower(), text.count("\n", 0, m.start()) + 1) for m in WORD.finditer(text)]
    return [tokens[i][1] for i in range(len(tokens) - N + 1)
            if tuple(t for t, _ in tokens[i:i + N]) in corpus]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--baseline-rev", default="", help="the commit before this slice (1f6120e)")
    ap.add_argument("--baseline-path", action="append", default=[])
    ap.add_argument("files", nargs="+")
    args = ap.parse_args(argv)
    corpus = archive_shingles(Path(args.run))
    print(f"archive shingles ({N} words, whole files): {len(corpus)}")
    if args.baseline_rev:
        paths = args.baseline_path or ["src", "benchmarks/expertlongbench", "docs"]
        base = baseline_shingles(REPO, args.baseline_rev, paths)
        corpus -= base
        print(f"baseline {args.baseline_rev} ({', '.join(paths)}): {len(base)} shingles; "
              f"archive-only shingles {len(corpus)}")
    hits = 0
    for name in args.files:
        starts = shared_runs(Path(name).read_text(encoding="utf-8"), corpus)
        hits += len(starts)
        for no in sorted(set(starts)):
            print(f"HIT {name}: {starts.count(no)} shared {N}-word run(s) starting on line {no}")
    print(f"{'FAIL' if hits else 'clean'}: {hits} shared run(s) over {len(args.files)} file(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
