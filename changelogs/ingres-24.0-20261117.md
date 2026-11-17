# Neo OS 0.4 Beta — POCO F4 GT / Redmi K50 Gaming (`ingres`)

> **Pre-release.** Back up your data before flashing. Updating from 0.3 through the Updater keeps your data.

LineageOS 24.0 (Android 17) · Linux 6.6.144 GKI vendor kernel · Security patch 2026-10-01

## Highlights
- **Faster kernel:** system calls +26%, Wine/Proton sync (ntsync) +9–40%, Vulkan dispatch +9–20%
- **Pixel experience:** Pixel Launcher, Circle to Search, a working At a Glance, Google Sans Flex
- **Native haptics:** a vibrator HAL built for the F4 GT's motor, with crisp tuned effects and the full Android haptics API
- **A redesigned Neo Parts** with a Monet colour engine, game performance mode and three-finger screenshot
- **AOD fixed:** no more bright flash when waking from always-on display

## Performance
- **Lighter kernel hardening.** Turned off four security checks that cost time on every system call or kernel function: hardened usercopy, Spectre branch-history clearing, kernel stack randomization and kernel pointer authentication. Apps keep their own pointer authentication.
- **ThinLTO + a new AutoFDO profile.** The kernel is optimized with a profile recorded on this phone, and it now also covers the GPU, display and ntsync drivers.
- **Measured gains** (kernel micro-benchmarks, clocks locked, median of 7 runs, compared with 0.3):

| Test | Gain |
|---|---|
| System calls | **+26%** |
| ntsync (Wine / Proton games) | **+9–40%** |
| Vulkan dispatch (GPU driver) | **+9–20%** |
| Cross-core wake-ups (sync-wake + game mode) | **up to 6× faster** |

  18 of 21 benchmarks are faster on average across the three core types. One trade-off: large reads from RAM-backed files are about 10% slower; this is being investigated.
- **Game performance (Neo Parts → Gaming):** sets a minimum CPU speed for the games you choose and gives the game in front latency-sensitive scheduling.

## Pixel experience
- **Pixel Launcher built in.** It draws the home screen, recent apps, the taskbar and the navigation bar. The old LineageOS launcher has been removed.
- **Circle to Search:** long-press the navigation handle or home button. It plays a short "pop" haptic instead of a long buzz.
- **At a Glance works.** Weather and cards from the Google app now appear; before, it showed only the date. It also has:
  - Battery cards for connected earbuds and watches
  - A flashlight card while the flashlight is on, with a tap-to-turn-off chip
  - Upcoming alarms, calendar events and other Google cards
- **Android System Intelligence** has all its Pixel roles: Live Caption, translation, smarter autofill and more.
- **Google Play services can now deliver feature flags** to Android System Intelligence, so Google's server-side Pixel features can turn on.
- **Live Updates:** running timers and stopwatches show as a countdown chip in the status bar and on the lock screen, as on Pixels.
- **Google Sans Flex** is the system font.
- **Google Photos** sees an original Pixel XL, so it offers free unlimited original-quality backup. This needs spoofing turned on for Photos in Neo Parts.

## Native haptics
- **A new vibrator HAL for the F4 GT's own haptic driver** (Awinic AW86927), replacing Qualcomm's generic vibrator service.
- **Waveforms designed for this motor.** Every effect is synthesized for the motor's resonance and streamed to the driver directly, instead of using stock presets. Each tap ends with a short braking pulse, so it stops instantly instead of buzzing.
- **The full Android haptics API:** click, double click, heavy click, tick, texture tick, thud and pop effects; the composition primitives (click, light tick, low tick, quick rise, quick fall, slow rise, spin, thud); amplitude control. Apps and games that use rich haptics now get their real effects instead of a generic buzz.
- The shoulder triggers and Circle to Search play the crisp "pop".

## Neo Parts
- A new **Settings-style home screen** with grouped pages and coloured icons
- **Monet engine:** colour styles, custom colours and a live preview
- **Game performance:** per-game CPU floor (see Performance)
- **Three-finger screenshot**
- **Haptics page:** feel-test every effect and set the master vibration strength
- **Diagnostics:** log capture and a battery recorder for tracking down shutdowns
- Fixed: the trigger overlay's auto-edit no longer gets stuck

## Display and unlock
- **AOD wake flash fixed:** waking from always-on display no longer flashes the clock brighter, and the fade to the lock screen stays smooth.
- **AOD stays on reliably** instead of dropping out early.
- **Face + fingerprint together:** biometric prompts open with both ready. While face unlock scans, a sweeping arc is shown.

## Fixes
- **Battery level guard (kernel):** the battery percentage can no longer stay far above the real charge. Some testers saw the phone shut down at 36–74%; the reported level now follows the battery gauge, and the phone powers off cleanly when it is really empty.
- At a Glance's weather settings page no longer crashes.
- The flashlight tile and At a Glance now use the same camera, so the flashlight card appears reliably.
- Event-only buttons on At a Glance cards no longer show "App isn't installed".

## Branding
- "LineageOS" is now **"Neo OS"** in setup, the Updater and Settings.

## Known issues
- Ultrasound proximity ("hand wave to wake") does not report near yet.
- **Now Playing** (song recognition) is off: it needs Pixel's always-listening audio chip, and the normal-microphone fallback costs too much battery.
- **The Pixel Weather app** needs Google's weather servers, which some networks and DNS services block. There it fails to sign in; a VPN or another network fixes it. At a Glance weather is not affected.
- **Google Clock from the Play Store** may start with notifications blocked. Allow them to get timer chips.
- Some testers still report random shutdowns. If it happens to you, please send a log from Neo Parts.

## Install
- **From 0.3:** Updater → check for updates, or Updater → ⋮ → Local update with the downloaded zip.
- **Fresh install:** flash from recovery, as with earlier releases.
