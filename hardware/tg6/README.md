# Olympus Tough TG-6 — capture camera for % cover monitoring

The **Olympus Tough TG-6** was the camera used by divers to photograph each
housing for the **biofilm % cover monitoring** survey (and the optical-clarity
port images). This folder documents the camera, the raw format, and the exact
rendering geometry used downstream, with an official spec sheet and one sample
RAW frame for anyone reproducing the pipeline.

## Contents
- `TG-6_Olympus_press_specs_2019.pdf` — official Olympus launch spec sheet (source below).
- `samples/P8210005.ORF` — one unmodified raw frame (11 MB) to run the pipeline end-to-end.

## Key specifications

| Property | Value | Source |
|---|---|---|
| Sensor | 1/2.3″ BSI-CMOS, 6.17 × 4.55 mm | spec sheet |
| Effective resolution | 12 MP (nominal 4000 × 3000 px) | spec sheet |
| Image processor | TruePic VIII | spec sheet |
| Lens | 4.5–18 mm (25–100 mm equiv.), f/2.0–4.9, 4× optical | spec sheet |
| ISO | 100–12800 | spec sheet |
| Video | 4K/30p, FHD/120fps | spec sheet |
| Rugged | Waterproof 15 m, shock 2.1 m, crush 100 kgf, freeze −10 °C | spec sheet |
| **Raw format** | **Olympus `.ORF`, 12-bit** | raw metadata |
| **Color-filter array** | **Bayer RGGB** | raw metadata |
| **Full (active) raw array** | **4014 × 3016 px** | LibRaw render of sample |
| **Half-resolution output (`-h`)** | **2007 × 1508 px** | LibRaw render of sample |

> **Important for methods:** the Bayer **RGGB** pattern and the exact raw
> geometry are *not* on any consumer spec sheet (which lists only the nominal
> 4000 × 3000 output). They were read directly from the raw file. The
> half-resolution grayscale pipeline (see [`../../preprocessing/`](../../preprocessing/))
> maps each 2 × 2 Bayer quad to one pixel, giving the confirmed **2007 × 1508**
> output used for all analysis.

## Reproduce the raw geometry

```bash
# Full-res active area and half-res output (LibRaw):
dcraw_emu -h -T -4 -r 1 1 1 1 -o 0 -Z - samples/P8210005.ORF | magick - -format "%wx%h" info:
#  -> 2007x1508

# Camera / CFA / capture metadata:
exiftool -Make -Model -CFAPattern2 -BitsPerSample -ISO -FNumber \
         -ExposureTime -FocalLength -DateTimeOriginal samples/P8210005.ORF
```

## Sources
- Olympus Tough TG-6 launch spec sheet (PDF): https://www.olympus-global.com/news/2019/contents/nr01264/nr01264_00001.pdf
- Full specifications (DPReview): https://www.dpreview.com/products/olympus/compacts/olympus_tg6/specifications
- Overview (Wikipedia): https://en.wikipedia.org/wiki/Olympus_Tough_TG-6
