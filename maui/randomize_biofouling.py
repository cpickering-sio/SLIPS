#!/usr/bin/env python3
"""
Biofouling Image Randomization Script
Thode Lab — SLIPS Project | Ulua Beach, Maui 2026

HOW TO USE:
  1. Set BASE_DIR to your Ulua_beach folder path
  2. Run: python3 randomize_biofouling.py
  3. Script will:
       - Walk each date subfolder (e.g. 03292026/, 04132026/, 04192026/)
       - Auto-assign camera number from filename (e.g. GOPR0405_3.JPG -> cam 3)
       - Tag housing shots (no _#) by associating with nearest flange camera
       - Label each image as treatment / control / factory_standard_acrylic
       - Assign a unique 6-character random ID to every image
       - Copy renamed images into  blinded_images/  folder
       - Save  randomization_key.csv      <- YOU KEEP THIS, do not share
       - Save  analyzer_image_list.csv    <- share with analyzer

DO NOT share randomization_key.csv until all scoring is complete.
"""

import os, re, csv, random, string, shutil

# ── SETTINGS ──────────────────────────────────────────────────────────────────

BASE_DIR = "/Users/corinnepickering/Desktop/Thode_lab/SLIPS/maui2026/Ulua_beach"

CONDITION_MAP = {
    "1":  "treatment",
    "2":  "treatment",
    "3":  "treatment",
    "4":  "control",
    "6":  "control",
    "12": "control",
    "7":  "factory_standard_acrylic",
    "10": "factory_standard_acrylic",
    "11": "factory_standard_acrylic",
}

OUTPUT_KEY      = os.path.join(BASE_DIR, "randomization_key.csv")
OUTPUT_ANALYZER = os.path.join(BASE_DIR, "analyzer_image_list.csv")
BLINDED_DIR     = os.path.join(BASE_DIR, "blinded_images")

RANDOM_SEED = 42   # Keep this number recorded -- same seed = same IDs if you need to regenerate
ID_LENGTH   = 6

# ── HELPERS ───────────────────────────────────────────────────────────────────

def parse_camera_number(filename):
    """Extract camera number from GOPR####_#.JPG format. Returns None if no _# present."""
    match = re.search(r'_(\d+)\.\w+$', filename)
    return match.group(1) if match else None

def assign_groups(file_list):
    """
    Assign camera number and image type to every file in a date folder.
    - Files WITH _# -> flange shot, camera = that number
    - Files WITHOUT _# -> housing shot, camera = nearest labeled file
      (looks forward first, then backward)
    """
    labeled = {i: parse_camera_number(f) for i, f in enumerate(file_list)
               if parse_camera_number(f)}
    result = []
    for i, filename in enumerate(file_list):
        cam = parse_camera_number(filename)
        if cam:
            img_type = "flange"
        else:
            img_type = "housing"
            cam = None
            for j in range(i + 1, len(file_list)):
                if j in labeled:
                    cam = labeled[j]; break
            if cam is None:
                for j in range(i - 1, -1, -1):
                    if j in labeled:
                        cam = labeled[j]; break
        result.append((filename, cam or "unknown", img_type))
    return result

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

    skip_dirs = {"blinded_images"}

    for date_folder in sorted(os.listdir(BASE_DIR)):
        date_path = os.path.join(BASE_DIR, date_folder)
        if not os.path.isdir(date_path) or date_folder in skip_dirs:
            continue

        images = sorted([f for f in os.listdir(date_path)
                         if f.lower().endswith((".jpg",".jpeg",".png",".tif",".tiff"))])
        if not images:
            continue

        grouped = assign_groups(images)

        for filename, cam, img_type in grouped:
            condition = CONDITION_MAP.get(cam, "unknown -- add to CONDITION_MAP")
            ext = filename.rsplit(".", 1)[-1]
            rid = generate_random_id(ID_LENGTH, used_ids)
            records.append({
                "random_id":         rid,
                "new_filename":      f"{rid}.{ext}",
                "original_date":     date_folder,
                "camera_number":     cam,
                "image_type":        img_type,
                "condition":         condition,
                "original_filename": filename,
                "original_path":     os.path.join(date_path, filename),
            })

    if not records:
        print("No images found. Check BASE_DIR path.")
        return

    # Shuffle so analyzer sees no date/camera ordering
    analyzer_records = [{"random_id": r["random_id"], "new_filename": r["new_filename"]}
                        for r in records]
    random.shuffle(analyzer_records)

    # Save researcher key
    key_fields = ["random_id","new_filename","original_date","camera_number",
                  "image_type","condition","original_filename"]
    with open(OUTPUT_KEY, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=key_fields)
        w.writeheader()
        for r in records:
            w.writerow({k: r[k] for k in key_fields})
    print(f"Researcher key    -> {OUTPUT_KEY}")

    # Save blinded analyzer list
    with open(OUTPUT_ANALYZER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["random_id","new_filename"])
        w.writeheader()
        w.writerows(analyzer_records)
    print(f"Analyzer list     -> {OUTPUT_ANALYZER}")

    # Copy renamed images into blinded_images/
    os.makedirs(BLINDED_DIR, exist_ok=True)
    for r in records:
        shutil.copy2(r["original_path"], os.path.join(BLINDED_DIR, r["new_filename"]))
    print(f"Blinded images    -> {BLINDED_DIR}")

    # Summary
    dates   = sorted(set(r["original_date"] for r in records))
    cameras = sorted(set(r["camera_number"] for r in records), key=lambda x: int(x) if x.isdigit() else 99)
    print(f"\n   Total images randomized : {len(records)}")
    print(f"   Date folders processed  : {dates}")
    print(f"   Cameras found           : {cameras}")
    print(f"\n   Condition breakdown:")
    for cond in ["treatment", "control", "factory_standard_acrylic"]:
        n = sum(1 for r in records if r["condition"] == cond)
        print(f"     {cond:30s}: {n} images")
    print(f"\n   Lock away randomization_key.csv -- do not share until scoring is complete.")

if __name__ == "__main__":
    main()
