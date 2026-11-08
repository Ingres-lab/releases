# Neo OS 0.1 Beta — POCO F4 GT / Redmi K50 Gaming (`ingres`)

> **Pre-release.** First public build of Neo. Expect rough edges. Back up everything before flashing.

LineageOS 24.0 (**Android 17**), with a **Linux 6.6.144 GKI** vendor kernel (Sony `msm-6.6` base adapted to Xiaomi) in place of the stock 5.10 kernel.

| | |
|---|---|
| Android | 17 (SDK 37), LineageOS 24.0 |
| Security patch | 2026-10-01 |
| Kernel | 6.6.144, Neo `perf` profile (ThinLTO, clang 22) |
| Vendor / firmware base | MIUI `OS2.0.5.0.ULJCNXM` |
| Build | `userdebug`, signed with Neo release keys |
| Install | A/B OTA (Virtual A/B) |

## What Neo adds

### Neo settings (NeoParts, Settings → Neo)
- **Shoulder triggers:** map the left and right magnetic triggers to touch points, with an on-screen point editor and a Quick Settings tile
- **Rear lights:** per-event colours and effects for calls, notifications, low battery and charging (priority call > notification > low > charging), brightness, speed, custom colour and a glow while booting. New lights HAL `android.hardware.lights-service.neo`
- **Bypass charging:** powers the phone directly from the charger, so the battery isn't charged while gaming. Includes a live battery-current monitor
- **Mesa Turnip Vulkan driver:** switch between Turnip and the Adreno driver (applied on reboot)
- **Smooth motion video:** per-app setting with adjustable strength
- **SELinux toggle:** enforcing (default) or permissive
- Neo boot animation and wallpaper (set on first boot)

### Kernel (6.6 GKI)
- **KernelSU-Next v3.4.2** built in (root)
- **NTSync** (`/dev/ntsync`, backported from 6.17) with a WF_SYNC wake hint for Wine/Proton. Verified in Winlator with Proton 11 (`WINENTSYNC=1`)
- **120 Hz** command mode fixed (RSC prefill), 1:1 refresh confirmed
- WALT scheduler and EPSS cpufreq working (policies 1.79 / 2.50 / 3.00 GHz)
- Default qdisc `fq` (for BBR pacing), zram `lz4`
- User namespaces + checkpoint/restore (containers)
- **USB Wi-Fi dongles over OTG**, monitor mode and injection: MT7601U, MT7612U, rtw88 (8822BU / 8821CU / 8822CU / 8723DU), RTL8812AU / 8821AU / 8814AU (aircrack-ng driver). Firmware included
- USB RNDIS tethering; RTL-SDR driver built but not loaded, so SDR apps keep the dongle
- Ported Xiaomi drivers: ST FTS touch (report-rate read), xm_gamekey (hall sysfs), qti_battery_charger, mi_thermal, aw86927 haptics, aw22xxx LEDs, IR blaster, fpc1540 fingerprint
- `arm64.nosve arm64.nosme` on the kernel command line

### Device
- Xiaomi camera (MiuiCamera) working: the compute DSP now boots via `cdsp-loader`, and the camera has its Android 17 `platform_app_36` policy
- Recovery boots on 6.6 (strict first-stage module list fixed)
- Flash LED / torch, USB role switch (replug), GPS, cellular data, IR TX
- Updater: OTAs from this repository (Settings → System → Updater)

## Known issues
- Calls, Wi-Fi connect, photo capture on all lenses, video record/playback: **not fully tested yet**
- GPU logs non-fatal `AHB bus error` bursts (no visible effect so far)
- Display ESD recovery is disabled
- Quick Settings tiles may briefly show "!"
- This build trusts the maintainer's adb key (developer convenience); adb still has to be enabled by you

## Install
Clean flash only (Neo uses its own signing keys and a different kernel, so the data has to be wiped):
1. Unlocked bootloader. Back up your data.
2. `fastboot flash boot boot.img`, `fastboot flash vendor_boot vendor_boot.img`, `fastboot flash dtbo dtbo.img`, `fastboot flash recovery recovery.img`, `fastboot flash vbmeta vbmeta.img`
3. `fastboot reboot recovery` → Factory reset → Format data
4. Apply update → ADB sideload → `adb sideload Neo-24.0-20261107-ingres.zip`
5. Reboot

Check each file against its `.sha256`.

Kernel source and kernel images: <https://github.com/Ingres-lab/android_kernel_xiaomi_sm8450/releases>
