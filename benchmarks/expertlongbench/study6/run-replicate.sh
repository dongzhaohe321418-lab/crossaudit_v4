#!/bin/sh
# Study 6 -- one replicate of the audit-stage noise floor, plus bounded retries of any
# audit call that never reached a provider.
#
#   sh benchmarks/expertlongbench/study6/run-replicate.sh <label> [max-fill-passes]
#
# The replicate itself is `premise.py --rejudge`, unchanged. A fill pass re-asks ONLY the
# instances whose call failed before a model answered (see --only-unreached-in); an
# auditor that replied is never re-asked, so no result can be selected on. Fill passes
# stop when there is nothing left to retry or the cap is reached; `noise_report.py` joins
# a replicate's rows with its fills.
set -e
W="$(cd "$(dirname "$0")/../../.." && pwd)"
R="$W/benchmarks/expertlongbench/runs"
ARCHIVE="${STUDY6_ARCHIVE:-/Users/ericdong/Documents/Crossaudit/study-data/wt-split-runs/armX-split}"
LABEL="$1"
MAX_FILL="${2:-3}"
COMMON="--task T03MaterialSEG --n 20 --seed 20260930 --arms cross"

export PYTHONPATH="$W/src"

if [ ! -d "$R/$LABEL" ]; then
  python3 "$W/benchmarks/expertlongbench/premise.py" $COMMON \
      --rejudge "$R/study6-source" --label "$LABEL" --out "$R/$LABEL"
fi

prev="$R/$LABEL"
k=1
while [ "$k" -le "$MAX_FILL" ]; do
  src="$R/study6-source-${LABEL}-fill$k"
  out="$R/$LABEL-fill$k"
  if ! python3 "$W/benchmarks/expertlongbench/noise_source.py" \
        --archive "$ARCHIVE" --out "$src" --only-unreached-in "$prev" \
        | tee /dev/stderr | grep -q "nothing to retry"; then
    [ -d "$out" ] || python3 "$W/benchmarks/expertlongbench/premise.py" $COMMON \
        --rejudge "$src" --label "$LABEL-fill$k" --out "$out"
    prev="$out"
    k=$((k + 1))
  else
    break
  fi
done
echo "replicate $LABEL complete (fill passes used: $((k - 1)))"
