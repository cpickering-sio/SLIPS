#!/bin/bash
# SLIPS ORF -> half-res LINEAR 16-bit grayscale TIFF batch converter
# Keeps originals; writes copies to a parallel *_grayscale_linear folder tree.
# LINEAR output (-4) is required for physically valid contrast (CTF) analysis.
set -u

# --- edit these two paths for a new deployment if needed ---
SRC="/Volumes/samsung/Corinne/SLIPS082026/MONITORING"
DST="/Volumes/samsung/Corinne/SLIPS082026/MONITORING_grayscale_linear"
# -----------------------------------------------------------

LOG="${DST}/conversion_log.txt"
mkdir -p "$DST"
: > "$LOG"

total=$(find "$SRC" -type f -iname '*.orf' ! -name '._*' | wc -l | tr -d ' ')
echo "Total ORF files to process: $total" | tee -a "$LOG"
count=0

find "$SRC" -type f -iname '*.orf' ! -name '._*' -print0 | while IFS= read -r -d '' f; do
  rel="${f#"$SRC"/}"
  reldir="$(dirname "$rel")"
  stem="$(basename "$f")"; stem="${stem%.*}"
  outdir="$DST/$reldir"; mkdir -p "$outdir"
  out="$outdir/${stem}_graylin.tiff"
  count=$((count+1))

  # skip if a non-empty output already exists (so re-runs only do new dives)
  if [ -s "$out" ]; then
    echo "[$count/$total] SKIP (exists) $rel" >> "$LOG"
    continue
  fi

  # dcraw_emu flags:
  #   -h  half-size (each RGGB quad -> one pixel, NO debayer interpolation)
  #   -T  TIFF
  #   -4  LINEAR 16-bit (== -6 -W -g 1 1): no gamma, no auto-bright -> true intensity
  #   -r 1 1 1 1  unity white balance (identical treatment across all shots)
  #   -o 0  raw camera colorspace (no matrix rotation)
  #   -Z -  write to stdout (never pollutes source folders)
  if dcraw_emu -h -T -4 -r 1 1 1 1 -o 0 -Z - "$f" 2>>"$LOG" \
       | magick - -grayscale Average -depth 16 "$out" 2>>"$LOG" && [ -s "$out" ]; then
    echo "[$count/$total] OK  $rel -> ${stem}_graylin.tiff" >> "$LOG"
  else
    echo "[$count/$total] FAIL $rel" >> "$LOG"
  fi
done

ok=$(grep -c ' OK ' "$LOG"); bad=$(grep -c ' FAIL ' "$LOG"); skip=$(grep -c ' SKIP ' "$LOG")
echo "DONE. Converted OK: $ok  Skipped (already existed): $skip  Failures: $bad" | tee -a "$LOG"
