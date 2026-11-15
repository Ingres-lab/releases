# Neo OS 0.3 Beta — POCO F4 GT / Redmi K50 Gaming (`ingres`)

> **Pre-release.** Back up everything before flashing.

LineageOS 24.0 (Android 17) with the Linux 6.6.144 GKI vendor kernel, now built with a profile-guided (AutoFDO) kernel.

## What's new since 20261114
- **Profile-guided kernel (AutoFDO):** the kernel is optimised with a profile recorded on the phone itself (CoreSight ETE trace). Measured kernel micro-benchmark gain: +13% / +6% / +7% geometric mean on the A510 / A710 / X2 cores, with 23% fewer instruction-cache misses on process exec. Real-world gain is expected to be smaller (a few percent). `-mtune=cortex-a710` is also enabled (no measurable effect).
- **GPU "AHB bus error" fixed:** the Adreno 730 now gets its `CP_AHB_CNTL` default-slave setting; the error no longer appears in the kernel log.
- **AOD to lock screen:** no more full-brightness flash when leaving AOD.
- **Dolby:** DMS 2.0 HAL VINTF matrix and sepolicy fixed (no crash loop).
- **Neo Parts:** the trigger overlay shows over any app (including Files), the trigger editor no longer crashes, the SELinux switch keeps its state, and Color accuracy now applies an accurate sRGB mode.
- Telephony and VoIP audio priority tweaks.
- Recovery images carry the touch driver, so touch works in recovery.

## Known issues
- Ultrasound proximity ("hand wave to wake") does not report near yet.
- Some testers still report random shutdowns; logs are being analysed.
