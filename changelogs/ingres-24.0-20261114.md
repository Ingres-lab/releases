# Neo OS 0.2 Beta — POCO F4 GT / Redmi K50 Gaming (`ingres`)

> **Pre-release.** Second public build of Neo. Back up everything before flashing.

LineageOS 24.0 (**Android 17**) with the **Linux 6.6.144 GKI** vendor kernel.

| | |
|---|---|
| Android | 17 (SDK 37), LineageOS 24.0 |
| Security patch | 2026-10-01 |
| Kernel | 6.6.144, Neo `perf` profile (ThinLTO, clang 22) |
| Vendor / firmware base | MIUI `OS2.0.5.0.ULJCNXM` |
| Build | `userdebug`, signed with Neo release keys |
| Install | A/B OTA (Virtual A/B) |

## What's new since 0.1 (20261107)

### Google apps and face unlock
- **MindTheGapps built in** when the local `vendor/gapps` tree is present. The default runtime
  grants for GMS and the sync adapters are applied on first boot, which a GApps zip flashed after
  first boot never gets (contacts/calendar sync then stays off).
  The Google app (`Velvet`, ~243 MB) is not included in this build so the OTA stays under GitHub's
  2 GiB release-asset limit.
- **Face unlock** through ParanoidSense/FaceService, declared as
  `android.hardware.biometrics.face`. Built only when the local `packages/apps/FaceUnlock` tree is
  present.

### Dolby Atmos
- Dolby DAX3 with the DMS 2.0 HAL and the LunarisDolby app, including the ingres DAX tuning
  (with `speaker_landscape_180`) and Dolby's spatializer. Dolby's volume listeners replace the
  volume post-processing for music/ring/alarm/notification.
- `media_codecs_taro.xml` with the Dolby codec include.

### NeoParts (Settings → Neo)
- **Tools → Play Integrity:** load a `pif.json` (from this repository or a file) into
  `persist.sys.neo.pif.*`, see the loaded device, clear it, or switch the spoof off. DroidGuard is
  restarted to pick it up.
- **Tools → Pixel features:** per-app Pixel 10 Pro XL spoof for Google apps that gate features on
  Pixel hardware, plus extra apps to cover.
- **Tools → Hide developer options:** chosen apps read developer options, USB and wireless debugging
  as off.
- **Always-on display modes:** off / always / scheduled / for N seconds after screen-off, and
  show on hand wave (a short near→far on the proximity sensor). Turning AOD off from an app now
  applies immediately, even mid-doze.
- **Smooth motion video:** per-app motion-compensated frame interpolation on the DSP.
- **Display → Color accuracy:** switches the panel's flat calibration (`persist.sys.neo.flat`); it
  survives screen-off.
- **Shoulder triggers:** the point editor is now a floating overlay drawn above the running game
  instead of an Activity, so mapping no longer pauses or rotates the game. Optional draggable
  floating trigger button; the Quick Settings tile opens the overlay editor.
- **Bypass charging:** reports "not holding" only after 10 consecutive samples above the hold level.
- Neo wallpaper is generated and set on first boot.

### Framework and system
- **NeoPropHooks:** per-app Pixel feature flags and a Play Integrity `pif.json` spoof, applied only
  inside the target processes. No keybox and no native property hook.
- **SettingsProvider:** hides developer options from the apps chosen in NeoParts.
- **SystemUI:** DozeTriggers applies `doze_always_on` changes while dozing.
- **frameworks/av:** MediaCodec hook for the smooth motion video setting.

### Device and kernel
- **NFC:** NXP SN1xx driver loaded (`/dev/nq-nci`), so the NXP NFC HAL initializes.
- **Compute DSP:** `cdsp-loader` starts the CDSP at early boot. Camera AI nodes and the Qualcomm
  NNAPI HAL (HTP v69) work instead of failing with `ECONNREFUSED`.
- **EVA/CVP:** DSP-side dma-buf fds are resolved through the fastrpc HLOS tgid.
- **More USB Wi-Fi dongles over OTG** (monitor mode / injection): rtw88 8822BU / 8821CU / 8822CU /
  8723DU, MT7612U and the aircrack-ng RTL8812AU / 8821AU / 8814AU driver. Firmware included.
- **Kernel ASB-2026-11-02 merged** (78 commits, November 2026 security bulletin).
- **Battery charge counter fixed:** the ADSP reports µAh, but Xiaomi's driver multiplied by 1000
  (nAh), overflowing `intval` above ~2147 mAh. Above ~47% the charge counter went negative in
  Android and batterystats.
- **Panel fixes:** the L10 backlight is restored when leaving AOD (no white flash on wake), and the
  requested flat/color-accuracy mode is kept across panel power-off.
- Default qdisc `fq`, default zram compressor `lz4`.
- Settings now shows the kernel build date correctly (`uname -v` starts with an English weekday).
- Second stage no longer loads `icnss2` and `qcom_logbuf_vendor_hooks` (WCN6855 uses `cnss2`).
- Lineage Health removed: NeoParts is the only owner of the bypass-charging node, so it is no
  longer reset at boot.

## Known issues
- Calls, Wi-Fi connect, photo capture on all lenses, video record/playback: **not fully tested yet**
- GPU logs non-fatal `AHB bus error` bursts (no visible effect so far)
- Display ESD recovery is disabled
- Quick Settings tiles may briefly show "!"
- This build trusts the maintainer's adb key (developer convenience); adb still has to be enabled
  by you

## Install
Clean flash only (Neo uses its own signing keys and a different kernel, so the data has to be wiped):
1. Unlocked bootloader. Back up your data.
2. `fastboot flash boot boot.img`, `fastboot flash vendor_boot vendor_boot.img`,
   `fastboot flash dtbo dtbo.img`, `fastboot flash recovery recovery.img`,
   `fastboot flash vbmeta vbmeta.img`
3. `fastboot reboot recovery` → Factory reset → Format data
4. Apply update → ADB sideload → `adb sideload Neo-24.0-20261114-ingres.zip`
5. Reboot

Check each file against its `.sha256`.
