#!/usr/bin/env python3
"""
In-Air Before/After Image Randomization Script
Thode Lab — SLIPS Project | Maui 2026

File naming convention: IMG_##XY.ext
  ## = camera number  (01, 02, 03, 04, 06, 07, 10, 11, 12)
  X  = image type     C = color bar | R = resolution target
  Y  = timing         B = before    | A = after

HOW TO USE:
  1. Confirm BASE_DIR below matches your In_Air_before_after folder path
  2. Run: python3 randomize_in_air.py
  3. Script will:
       - Parse every image in the folder for camera, type, and timing
       - Map camera number to condition (treatment / control / factory_standard_acrylic)
       - Assign a unique 6-character random ID to every image
       - Copy renamed images into  blinded_images/  folder
       - Save  randomization_key.csv      <- YOU KEEP THIS, do not share
       - Save  analyzer_image_list.csv    <- share with analyzer

DO NOT share randomization_key.csv until all scoring is complete.
"""

import os, re, csv, random, string, shutil

# ── SETTINGS ──────────────────────────────────────────────────────────────────

BASE_DIR = "/Users/corinnepickering/Desktop/Thode_lab/SLIPS/maui2026/In_Air_before_after"

CONDITION_MAP = {
    "01": "treatment",
    "02": "treatment",
    "03": "treatment",
    "04": "control",
    "06": "control",
    "12": "control",
    "07": "factory_standard_acrylic",
    "10": "factory_standard_acrylic",
    "11": "factory_standard_acrylic",
}

IMAGE_TYPE_MAP = {
    "C": "color_bar",
    "R": "resolution_target",
}

TIMING_MAP = {
    "B": "before",
    "A": "after",
}

OUTPUT_KEY      = os.path.join(BASE_DIR, "randomization_key.csv")
OUTPUT_ANALYZER = os.path.join(BASE_DIR, "analyzer_image_list.csv")
BLINDED_DIR     = os.path.join(BASE_DIR, "blinded_images")

RANDOM_SEED = 42   # Keep this recorded -- same seed = same IDs if you need to regenerate
ID_LENGTH   = 6

# ── HELPERS ───────────────────────────────────────────────────────────────────

# Matches: IMG_01CA.JPG, IMG_12RB.jpeg, etc.
FILENAME_RE = re.compile(r'^IMG_(\d{2})([CR])([BA])\.\w+$', re.IGNORECASE)

def parse_filename(filename):
    """
    Returns (camera_str, image_type_code, timing_code) or None if no match.
    camera_str is zero-padded two digits, e.g. '01', '12'.
    """
    m = FILENAME_RE.match(filename)
    if not m:
        return None
    cam, img_type, timing = m.group(1), m.group(2).upper(), m.group(3).upper()
    return cam, img_type, timing

def generate_random_id(length, used):
    chars = string.ascii_uppercase + string.digits
    while True:
        rid = ''.join(random.choices(chars, k=length))
        if rid not in used:
            used.add(rid)
            return rid

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    random.seed(RANDOM_SEED)
    used_ids = set()
    records  = []
    skipped  = []

    images = sorted([
        f for f in os.listdir(BASE_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))
    ])

    if not images:
        print("No images found. Check BASE_DIR path.")
        return

    for filename in images:
        parsed = parse_filename(filename)
        if parsed is None:
            skipped.append(filename)
            continue

        cam, img_type_code, timing_code = parsed
        condition  = CONDITION_MAP.get(cam, "unknown -- add to CONDITION_MAP")
        image_type = IMAGE_TYPE_MAP.get(img_type_code, img_type_code)
        timing     = TIMING_MAP.get(timing_code, timing_code)
        ext        = filename.rsplit(".", 1)[-1]
        rid        = generate_random_id(ID_LENGTH, used_ids)

        records.append({
            "random_id":         rid,
            "new_filename":      f"{rid}.{ext}",
            "camera_number":     cam,
            "image_type":        image_type,
            "timing":            timing,
            "condition":         condition,
            "original_filename": filename,
            "original_path":     os.path.join(BASE_DIR, filename),
        })

    if not records:
        print("No images matched expected naming pattern IMG_##XY.ext")
        return

    # Shuffle so analyzer sees no camera/condition ordering
    analyzer_records = [{"random_id": r["random_id"], "new_filename": r["new_filename"]}
                        for r in records]
    random.shuffle(analyzer_records)

    # Save researcher key
    key_fields = ["random_id", "new_filename", "camera_number", "image_type",
                  "timing", "condition", "original_filename"]
    with open(OUTPUT_KEY, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=key_fields)
        w.writeheader()
        for r in records:
            w.writerow({k: r[k] for k in key_fields})
    print(f"Researcher key    -> {OUTPUT_KEY}")

    # Save blinded analyzer list
    with open(OUTPUT_ANALYZER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["random_id", "new_filename"])
        w.writeheader()
        w.writerows(analyzer_records)
    print(f"Analyzer list     -> {OUTPUT_ANALYZER}")

    # Copy renamed images into blinded_images/
    os.makedirs(BLINDED_DIR, exist_ok=True)
    for r in records:
        shutil.copy2(r["original_path"], os.path.join(BLINDED_DIR, r["new_filename"]))
    print(f"Blinded images    -> {BLINDED_DIR}")

    # Summary
    cameras = sorted(set(r["camera_number"] for r in records),
                     key=lambda x: int(x) if x.isdigit() else 99)
    print(f"\n   Total images randomized : {len(records)}")
    print(f"   Cameras found           : {cameras}")
    print(f"\n   Condition breakdown:")
    for cond in ["treatment", "control", "factory_standard_acrylic", "unknown -- add to CONDITION_MAP"]:
        n = sum(1 for r in records if r["condition"] == cond)
        if n:
            print(f"     {cond:40s}: {n} images")
    print(f"\n   Image type breakdown:")
    for itype in ["color_bar", "resolution_target"]:
        n = sum(1 for r in records if r["image_type"] == itype)
        print(f"     {itype:40s}: {n} images")
    print(f"\n   Timing breakdown:")
    for t in ["before", "after"]:
        n = sum(1 for r in records if r["timing"] == t)
        print(f"     {t:40s}: {n} images")

    if skipped:
        print(f"\n   WARNING — {len(skipped)} file(s) skipped (name did not match IMG_##XY.ext):")
        for s in skipped:
            print(f"     {s}")

    print(f"\n   Lock away randomization_key.csv -- do not share until scoring is complete.")

if __name__ == "__main__":
    main()
