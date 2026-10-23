#!/bin/bash
# SLIPS ORF -> half-res 16-bit grayscale TIFF batch converter
# Keeps originals; writes copies to a parallel *_grayscale folder tree.
# Method: half-size (no debayer interpolation) + equal-average grayscale.
set -u

# --- edit these two paths for a new deployment if needed ---
SRC="/Volumes/samsung/Corinne/SLIPS082026/MONITORING"
DST="/Volumes/samsung/Corinne/SLIPS082026/MONITORING_grayscale"
# -----------------------------------------------------------

LOG="${DST}/conversion_log.txt"
mkdir -p "$DST"
: > "$LOG"

total=$(find "$SRC" -type f -iname '*.orf' ! -name '._*' | wc -l | tr -d ' ')
echo "Total ORF files to process: $total" | tee -a "$LOG"
count=0

find "$SRC" -type f -iname '*.orf' ! -name '._*' -print0 | while IFS= read -r -d '' f; do
  rel="${f#"$SRC"/}"                    # e.g. 1_08212026/P8210005.ORF
  reldir="$(dirname "$rel")"
  stem="$(basename "$f")"; stem="${stem%.*}"
  outdir="$DST/$reldir"; mkdir -p "$outdir"
  out="$outdir/${stem}_gray.tiff"
  count=$((count+1))

  # dcraw_emu flags:
  #   -h  half-size (each RGGB quad -> one pixel, NO cross-pixel debayer interpolation)
  #   -T  TIFF, -6 16-bit
  #   -r 1 1 1 1  unity white balance (identical treatment across all shots -> comparable)
  #   -o 0  raw camera colorspace (no matrix rotation), -W  no auto-brighten
  #   -Z -  write to stdout (never pollutes source folders)
  if dcraw_emu -h -T -6 -r 1 1 1 1 -o 0 -W -Z - "$f" 2>>"$LOG" \
       | magick - -grayscale Average -depth 16 "$out" 2>>"$LOG" && [ -s "$out" ]; then
    echo "[$count/$total] OK  $rel -> ${stem}_gray.tiff" >> "$LOG"
  else
    echo "[$count/$total] FAIL $rel" >> "$LOG"
  fi
done

ok=$(grep -c ' OK ' "$LOG"); bad=$(grep -c ' FAIL ' "$LOG")
echo "DONE. Converted OK: $ok  Failures: $bad" | tee -a "$LOG"
