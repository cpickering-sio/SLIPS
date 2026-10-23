# Converting Olympus ORF RAW files to TIFF (for ImageJ)

A step-by-step guide for turning a `.ORF` camera RAW file (Olympus TG-6) into a
16-bit TIFF that opens natively in ImageJ / Fiji.

Worked example file: `P8210005.ORF`

---

## Why this is needed
- ImageJ **cannot read the Olympus `.ORF` format** directly. If you try, it
  falls back to the *Import > Raw* dialog and shows a meaningless default size
  (e.g. 1280 x 960) that is **not** in the file.
- The ORF actually contains: the raw sensor data (4040 x 3016), a large embedded
  JPEG preview (3200 x 2400), and a thumbnail (160 x 120).
- Converting to TIFF first gives ImageJ a real, full-resolution 16-bit image.

---

## Step 1 - Install the conversion tool (one time only)
We use **LibRaw**, which provides the `dcraw_emu` command-line converter.

```bash
brew install libraw
```

Verify it installed:

```bash
dcraw_emu --version   # or: which dcraw_emu
```

(If you don't have Homebrew, install it from https://brew.sh first.)

---

## Step 2 - Go to the folder with your ORF file

```bash
cd /Users/corinnepickering/Desktop/Thode_lab/SLIPS
```

---

## Step 3 - Convert the ORF to a 16-bit TIFF

```bash
dcraw_emu -T -6 -q 3 -w P8210005.ORF
```

What each flag does:

| Flag  | Meaning                              | Effect                                   |
|-------|--------------------------------------|------------------------------------------|
| `-T`  | Output TIFF (not PPM)                | Produces a `.tiff` file                  |
| `-6`  | 16-bit output                        | Full 16-bit-per-channel depth            |
| `-q 3`| Demosaic quality 3 = AHD             | Highest-quality color interpolation      |
| `-w`  | Use camera (as-shot) white balance   | Colors match what the camera recorded    |

The tool writes the output as `P8210005.ORF.tiff`.

---

## Step 4 - Rename to a clean filename (optional)

```bash
mv P8210005.ORF.tiff P8210005.tiff
```

---

## Step 5 - Verify the result

```bash
magick identify P8210005.tiff
```

Expected output (this example file):

```
P8210005.tiff TIFF 4014x3016 4014x3016+0+0 16-bit sRGB
```

Reading that line:

- **Width  = 4014 pixels**
- **Height = 3016 pixels**
- **Offset = +0+0**  (x = 0, y = 0 - no crop offset)
- **Bit depth = 16-bit per channel** (48-bit RGB total)
- **Color space = sRGB**

Note: the width is 4014, slightly less than the raw sensor's 4040, because dcraw
trims a few masked border columns that are not part of the visible image.

---

## Step 6 - Open in ImageJ
`File > Open...` and choose `P8210005.tiff`. No plugin required.

---

## Alternative: settings for quantitative / intensity analysis
The command above applies sRGB gamma, an sRGB color matrix, and auto-brightness,
which are good for a normal-looking picture but distort pixel intensity values.
For measurements, use a **linear, un-brightened** conversion instead:

```bash
dcraw_emu -T -4 -o 0 -W P8210005.ORF
```

| Flag   | Meaning                                         |
|--------|-------------------------------------------------|
| `-4`   | 16-bit linear (no gamma) = `-6 -g 1 1`          |
| `-o 0` | Keep raw camera color space (no sRGB matrix)    |
| `-W`   | Disable auto-brightness (fixed white level)     |

For the true single-channel sensor values with **no demosaicing**, use `-D`
(document mode) or the `unprocessed_raw` tool that ships with LibRaw.

---

# Batch conversion: all ORFs -> half-res grayscale (for biofouling time-series)

Goal: compare biofouling on the SLIPS housings across deployment dates. Because
the images are shot underwater (~40 ft, surge, dive-light reflections), the plan
is to produce **clean, consistent grayscale** images suitable for thresholding /
percent-cover analysis in ImageJ, while **keeping all originals**.

## Source of the monitoring images
The full monitoring image set lives on the Samsung external drive:

```
/Volumes/samsung/Corinne/SLIPS082026/MONITORING
```

with one dated subfolder per deployment check:

```
1_08212026/   2_08282026/   3_09042026/   4_09102026/
```

Grayscale copies are written to a parallel tree (originals untouched):

```
/Volumes/samsung/Corinne/SLIPS082026/MONITORING_grayscale
```

## Why "half-size" instead of a normal color conversion
Each ORF pixel sits under a single color filter in a repeating 2x2 **Bayer**
pattern (Red, Green, Green, Blue). A normal conversion "**debayers**" this by
interpolating the two missing colors at every pixel - which can add artifacts.

To *avoid worrying about debayering*, we use dcraw's **half-size** mode (`-h`):
each 2x2 sensor quad collapses into **one** pixel with no cross-pixel guessing.
We then average the channels to a single gray value. Result: ~2007 x 1508,
16-bit grayscale, artifact-free. Half resolution is not a limitation here because
underwater motion blur already limits detail.

## The conversion command (per file)

```bash
dcraw_emu -h -T -6 -r 1 1 1 1 -o 0 -W -Z - INPUT.ORF | \
  magick - -grayscale Average -depth 16 OUTPUT_gray.tiff
```

| Flag         | Meaning                                                        |
|--------------|----------------------------------------------------------------|
| `-h`         | Half-size (RGGB quad -> 1 pixel, no debayer interpolation)     |
| `-T -6`      | 16-bit TIFF                                                     |
| `-r 1 1 1 1` | Unity white balance - every image treated identically (comparable across dates) |
| `-o 0`       | Raw camera colorspace (no color-matrix rotation)               |
| `-W`         | No auto-brighten (fixed levels - preserves relative intensity) |
| `-Z -`       | Write to stdout (never leaves temp files next to originals)    |
| `magick ... -grayscale Average` | Equal-weight average of channels -> grayscale |

## Running the whole batch
A ready-to-run script is saved in two places:

```
/Volumes/samsung/Corinne/SLIPS082026/slips_gray_batch.sh          (with the data)
.../SLIPS_Off_Pier_202608/Biofouling/slips_gray_batch.sh          (with this tutorial)
```

Run it with:

```bash
bash /Volumes/samsung/Corinne/SLIPS082026/slips_gray_batch.sh
```

It mirrors the subfolder structure into `MONITORING_grayscale/`, names each output
`<original>_gray.tiff`, and writes a `conversion_log.txt` in the output folder.
For a future deployment, edit the `SRC` and `DST` paths at the top of the script.

## Important caveat for the analysis
Grayscale conversion does **not** correct the differing reflections / lighting
between dates (a real issue given the dive-light and surge). That is a separate
downstream step - e.g. histogram matching between dates, or using the paired
light / no-light shots of each camera as references - done in ImageJ after this
conversion. This batch just creates the clean, consistent grayscale foundation.

---

# Analysis metric: CTF (port-surface contrast)

> The CTF method and original ImageJ macro are by **Nicholas Constantino**
> (<nconstantino@ucsd.edu>),
> https://github.com/nichconsta/SPC-Tools/blob/main/ImageJTools/CTFMacro.ijm.py
> The scripts here adapt and extend that work.

Divers survey the cage with the **Olympus TG-6**, photographing each **housing
port** of the autonomous cameras. The question this metric addresses is whether
the SLIPS coating keeps a port from fouling over time: **control** ports should
accumulate growth (contrast changes across dives) while **SLIPS-treated** ports
stay clear (contrast stable). Control vs. treatment is known from the camera ID.
(Assessing the autonomous cameras' *own* footage after retrieval is a separate,
later analysis.)

The metric is **Michelson contrast**, here called CTF:

```
CTF = (Imax - Imin) / (Imax + Imin)
```

measured on the **port surface** inside a chosen ROI. Imin and Imax are the mean
of the darkest and brightest fractions of pixels in the ROI. As fouling
accumulates on the port, the port's contrast changes over time.

> Direction is not assumed: biofilm haze can *lower* contrast by washing out
> features, while textured growth (e.g. barnacles) can *raise* it. Establish the
> direction empirically from the controls; the **control-vs-treatment difference
> over time** is the signal either way.

Why CTF is a good fit here:
- It is a **ratio**, so it is automatically invariant to overall
  exposure/brightness changes between dives (a dimmer dive scales Imax and Imin
  by the same factor, which cancels).

What CTF does NOT handle on its own (guard against these):
- **Additive backscatter / veiling light** (turbidity haze) adds a constant to
  every pixel and *lowers* CTF even with no new fouling. Subtract an estimate of
  it (the macro has a backscatter-offset option).
- **Glare / specular blowouts** inflate Imax. Exclude near-saturated pixels
  (the macro has a saturation-exclusion option) or use the no-light frame.
- **Non-linear (gamma) data** distorts Imin/Imax. See the next section.

## Why the analysis set must be LINEAR (-4, not -6)

CTF is only physically meaningful on pixel data that is **linear to scene
intensity**. Camera raw is linear off the sensor, but a normal conversion
(`-6`) re-applies a display **gamma curve**, which non-linearly compresses the
tonal scale and biases Imin/Imax (and therefore CTF). For quantitative work the
gamma must be removed - i.e. use dcraw's linear mode `-4` (equivalent to
`-6 -W -g 1 1`).

Supporting literature:
- Garcia, Dyer, Greentree & Dyer (2013), *PLoS ONE* 8(11):e79534 -
  "Linearisation of RGB Camera Responses for Quantitative Image Analysis of
  Visible and UV Photography." States that **linear camera responses are
  required** for recovering incident irradiance and for quantitative image
  analysis, because consumer cameras apply non-linear gain (gamma) in hardware
  and software. https://doi.org/10.1371/journal.pone.0079534
- Rodriguez Muina et al. (2025), *Chemical & Biomedical Imaging* -
  "Gamma Correction and Color Space Transformations for Quantitative Analysis of
  Electrochemiluminescence Images Using Smartphone Cameras." A direct **case
  study comparing the two**: gamma-encoded (BT.709) channel values were linear
  only up to a narrow range then bent into a power law, whereas the
  **gamma-inverted (linearised)** values were linear across the full 0-250 uM
  range (R2 = 0.996). https://doi.org/10.1021/cbmi.5c00056
- Burggraaff et al. (2019), "Standardized spectral and radiometric calibration
  of consumer cameras," documents that consumer cameras do not necessarily
  preserve linearity and must be calibrated. arXiv:1906.04155

The linear analysis set is at:
```
/Volumes/samsung/Corinne/SLIPS082026/MONITORING_grayscale_linear
```
files named `<original>_graylin.tiff` (2007 x 1508, 16-bit, linear).
NOTE: linear images look very dark on screen - that is correct. Adjust the
display only (ImageJ: Image > Adjust > Brightness/Contrast); do not "Apply",
which would alter the pixel data.

## Opening a linear grayscale TIFF in ImageJ / Fiji

Use **Fiji** (ImageJ bundled with plugins) - the CTF scripts need Fiji's Jython.
Download it from https://imagej.net/software/fiji if needed, then:

1. Launch Fiji.
2. **File > Open...** and choose a `*_graylin.tiff` from
   `.../MONITORING_grayscale_linear/<dive>/`. (Or drag the file onto the Fiji
   toolbar.)
3. **The image will look almost completely BLACK.** This is expected and correct
   for linear 16-bit data - nothing is wrong. Do not re-convert.
4. Fix the **display only**: **Image > Adjust > Brightness/Contrast...**
   (Cmd/Ctrl+Shift+C), then click **Auto**. This changes how the image is shown,
   not the pixel values.
   - DO NOT click **Apply** - that permanently rewrites the pixels and would
     corrupt the CTF measurement.
5. Zoom with `+` / `-` to frame the port.
6. Confirm the title bar shows `16-bit` (Image > Type should stay 16-bit).

> Never use **File > Import > Raw** for these - that is the trap that shows the
> bogus 1280 x 960 size. Always open the converted `.tiff`.

### Scripted alternative (ImageJ macro)

Instead of File > Open you can open by path from an ImageJ macro. This works:

```javascript
open("/Volumes/samsung/Corinne/SLIPS082026/MONITORING_grayscale_linear/1_08212026/P8210004_graylin.tiff");
selectImage("P8210004_graylin.tiff");
```

`open(...)` loads the file; `selectImage("<filename>")` makes it the active
window so the CTF script runs on the right image. The image is still linear
(dark) - adjust Brightness/Contrast for display as above before measuring.

## Running the CTF macro in Fiji

Script: `CTF_optical_clarity.py` (saved with this tutorial and on the Samsung
drive). It is a patched version of the original `Nicholas.txt`, fixing the ROI
mask and adding backscatter/glare handling. Steps:

1. Open a `_graylin.tiff` image in Fiji.
2. Draw the ROI over the port surface (any shape - the macro uses the
   true ROI mask, not just its bounding box).
3. `Plugins > Scripting > Script Editor`, open `CTF_optical_clarity.py`,
   language = Python, then Run.
4. In the dialog set: backscatter offset (0 unless you have an estimate),
   tail fraction (0.35), saturation value to exclude (e.g. 65535, or a measured
   glare threshold; 0 keeps all).
5. Read CTF from the Log; optionally save the pixel CSV.

Compare CTF for each port across the four dives, grouped by camera ID into
control vs. SLIPS-treated: controls should change over time (fouling) while
treated ports stay stable.

## Logging CTF to a spreadsheet (semi-automated)

The ROI must be placed **by hand** on every image - the port sits in a
different spot in each frame, so a fixed-coordinate oval would drift off-target.
Keep the oval **size** constant (e.g. 162 x 162) and move only its position, so
the measured area stays comparable. The script records ROI size for auditing.

Script: `CTF_measure_to_table.py` (with this tutorial and on the Samsung drive).
Per image:

1. Open a `_graylin.tiff`.
2. Draw the oval over the port surface (same size each time).
3. Run `CTF_measure_to_table.py`. Enter Camera #, Light (Y/N), notes; confirm.
4. A row is appended to one master CSV (default
   `/Volumes/samsung/Corinne/SLIPS082026/CTF_results.csv`).

Auto-filled: Folder, File_name, Monitoring Dive (parsed from folder), CTF, Imax,
Imin, ROI position/size, pixel count, and analysis parameters. The CSV header:

```
Camera #, Monitoring Dive, Light (Y/N), Folder, File_name, CTF,
Imax (top 35% average), Imin (bottom 35% average), notes,
ROI_x, ROI_y, ROI_w, ROI_h, N_pixels, Saturated_excluded,
Backscatter_offset, Tail_fraction, Timestamp
```

The first 9 columns match the manual sheet; the rest are provenance for
reproducibility (ignore or delete if unwanted). Choices (CSV path, last camera,
light, parameters) are remembered between runs to speed up repeated logging.

---

# References (BibTeX)

```bibtex
@article{garcia2013linearisation,
  author  = {Garcia, Jair E. and Dyer, Adrian G. and Greentree, Andrew D. and Spring, Gale and Wilksch, Philip A.},
  title   = {Linearisation of {RGB} Camera Responses for Quantitative Image Analysis of Visible and {UV} Photography: A Comparison of Two Techniques},
  journal = {PLoS ONE},
  year    = {2013},
  volume  = {8},
  number  = {11},
  pages   = {e79534},
  doi     = {10.1371/journal.pone.0079534}
}

@article{rodriguezmuina2025gamma,
  author  = {Rodr{\'i}guez Mui{\~n}a, Stephania and Gajjala, Rajendra Kumar Reddy and Fern{\'a}ndez Mart{\'i}n, Eduardo and del Campo, Francisco Javier},
  title   = {Gamma Correction and Color Space Transformations for Quantitative Analysis of Electrochemiluminescence Images Using Smartphone Cameras},
  journal = {Chemical \& Biomedical Imaging},
  year    = {2025},
  volume  = {3},
  number  = {11},
  pages   = {767--778},
  doi     = {10.1021/cbmi.5c00056}
}

@article{burggraaff2019standardized,
  author  = {Burggraaff, Olivier and Schmidt, Norbert and Zamorano, Jaime and Pauly, Klaas and Pascual, Sergio and Tapia, Carlos and Spyrakos, Evangelos and Snik, Frans},
  title   = {Standardized spectral and radiometric calibration of consumer cameras},
  journal = {Optics Express},
  year    = {2019},
  volume  = {27},
  number  = {14},
  pages   = {19075},
  doi     = {10.1364/OE.27.019075}
}
```

