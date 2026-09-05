#!/bin/sh
# Study 8 — archive the run directories and commit their digests.
#
# The run directories hold solution bytes, audit reports and revised files. They are
# deliberately outside the repository (EXPERIMENT_RECORD.md §3), so what travels with
# the paper is a per-file sha256 manifest and the digest of the manifest itself.
set -eu
RUN="${1:-$HOME/Documents/Crossaudit/study-data/wt-ceiling-runs}"
cd "$RUN"
find . -type f ! -name MANIFEST.sha256 -print0 \
  | sort -z \
  | xargs -0 shasum -a 256 > MANIFEST.sha256
echo "files: $(wc -l < MANIFEST.sha256)"
echo "manifest sha256: $(shasum -a 256 MANIFEST.sha256 | cut -d' ' -f1)"
