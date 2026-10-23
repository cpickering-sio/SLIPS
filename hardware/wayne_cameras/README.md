# Coral Cams — autonomous time-lapse cameras

Low-power underwater time-lapse cameras that recorded the footage used for the
**inner-cam underwater % cover** analysis
(see [`../../biofouling_cover/inner_cam/`](../../biofouling_cover/inner_cam/)).
The **Coral Cams** are a co-designed camera unit built with the Thode
Environmental Acoustics Laboratory (Scripps Institution of Oceanography) and
MakerBuoy Co.

**Full build, programming guides, Arduino sketches, libraries, and manufacturer
spec sheets:**
➡️ **https://github.com/cpickering-sio/Waynes_cameras**

## Hardware

| Component | Part / spec |
|---|---|
| Camera | **Spinel SC30MPA** serial JPEG camera (VC0706-protocol module) |
| Sensor | 3.0 MP, 1/2.7″ format, operated at max resolution **2304 × 1296** |
| Lens | **Spinel M12 S-mount, 3.6 mm, f/2.3** |
| Field of view (in air) | 120° diagonal × 96° horizontal × 72° vertical |
| Lens mount | custom 3D-printed holders (consistent lens angle across units) |
| Mainboard | **Maker Buoy** low-power platform (Wayne J. Pavalko — https://www.makerbuoy.com/) |
| Microcontroller | **Adafruit Feather M0** (SAMD21) — scheduler / intervalometer |
| Real-time clock | DS3231 |
| Storage | microSD (one JPEG per capture) |
| Power | 1S3P Li-ion pack, 3.7 V, 8700 mAh (powers mainboard + cameras) |
| Housing | acrylic pressure case (Blue Robotics, Inc.) |

## Capture schedule

- Feather M0 wakes on a **30-second standby cycle** to trigger acquisition.
- **Burst of 5 images (n = 5) every 30 minutes.**
- Daylight window nominally **07:00–17:00** (in practice continued to ~18:00).
- Dark frames skipped to conserve power over multi-day deployments.

## Verified toolchain (Aug 2026)

| Component | Version |
|---|---|
| Arduino IDE | 2.3.10 |
| Adafruit SAMD board package | 1.7.17 |
| Arduino SAMD core | 1.8.14 |

> Note: `Adafruit_VC0706` is a project-modified library — do **not** update it via
> the Library Manager. See the upstream repo's `SETUP.md`.

## Sources
- Coral Cams repository (sketches, guides, hardware spec-sheet PDFs): https://github.com/cpickering-sio/Waynes_cameras
- Maker Buoy platform (Wayne J. Pavalko): https://www.makerbuoy.com/

> Manuscript bibliography keys: camera `spinel_sc30mpa`, lens `spinel_m12_36mm`,
> microcontroller `adafruit_feather_m0`, RTC `ds3231`, mainboard `makerbuoy`,
> housing `BlueRobotics`.
