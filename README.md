# Neo releases

Builds of Neo, a LineageOS-based ROM, for the POCO F4 GT / Redmi K50 Gaming (`ingres`).

Download a build from [Releases](../../releases). Each zip has a matching `.sha256` next to it.

Updates also arrive through **Settings → System → Updater**, which reads [`ingres.json`](ingres.json).

## Publishing (maintainers)

```sh
./publish.py out/target/product/ingres/lineage-24.0-<date>-UNOFFICIAL-Neo-ingres.zip --changelog changelog.md
```

The script copies the zip to `out/Neo-24.0-<date>-ingres.zip`, writes the `.sha256` and creates the
GitHub Release. It then prepends the entry to `ingres.json`, taking the build time, SDK level, patch
level and A/B streaming offsets from the zip's `META-INF/com/android/metadata`, and pushes.
`--changelog` (alias `--notes`) is required; it becomes the release notes and is stored as
`changelogs/<tag>.md`, linked from the entry as `changelog_url` (the Updater ignores unknown keys).
`--dry-run` prints the `gh`/`git` commands without running them.

Kernel sets:

```sh
./publish_kernel.py out/target/product/ingres --profile perf --changelog kchangelog.md --min-rom <rom datetime or version>
```

Builds `out/Neo-kernel-<id>-ingres.zip` (+ `.sha256`), creates release `ingres-kernel-<id>`, stores the
changelog as `changelogs/kernel/<id>.md`, prepends the entry to `kernel/ingres.json` and pushes.
The kernel version comes from the `Linux version` banner in `boot.img` (or `--kernel-version`).

## Kernel channel format (for app authors)

`https://raw.githubusercontent.com/Ingres-lab/releases/main/kernel/ingres.json` is a JSON array, newest first:

```json
{
  "id": "6.6.144-neo-20261103-perf",
  "kernel_version": "Linux version 6.6.144-... (neo@ingres-lab) ...",
  "profile": "perf",
  "datetime": 1793710000,
  "min_rom": {"datetime": 1793700000},
  "download": {"filename": "Neo-kernel-6.6.144-neo-20261103-perf-ingres.zip",
               "url": "https://github.com/.../Neo-kernel-...zip", "sha256": "...", "size": 123456},
  "images": [
    {"partition": "vendor_dlkm", "filename": "vendor_dlkm.img", "logical": true,  "sha256": "...", "size": 0},
    {"partition": "vendor_boot", "filename": "vendor_boot.img", "logical": false, "sha256": "...", "size": 0},
    {"partition": "boot",        "filename": "boot.img",        "logical": false, "sha256": "...", "size": 0}
  ],
  "changelog": "markdown text",
  "changelog_url": "https://raw.githubusercontent.com/Ingres-lab/releases/main/changelogs/kernel/<id>.md"
}
```

- `id`: `<kernel x.y.z>-neo-<YYYYMMDD UTC>-<profile>`; `profile` is `perf` or `debug`; `datetime` is unix seconds.
- `min_rom`: either `{"datetime": N}` (install only if `ro.build.date.utc >= N`) or `{"version": "..."}`.
  The kernel's modules must match the ROM's vendor userspace; refuse older ROMs.
- The zip holds the three images and a `manifest.json` with the same `id`, `kernel_version`, `profile`,
  `datetime`, `min_rom` and `images` fields.
- `images` is listed in flashing order. `size`/`sha256` are of the raw (uncompressed) `.img`.

Verify: check the zip's `size` and `sha256` against `download`, extract, check every image's `size`
and `sha256` against `images`. Abort on any mismatch. The three images are one set: never flash a subset.

Flash, in order, to one slot `_a` or `_b` (the current slot, or the inactive one followed by switching
the active slot; the app chooses):

1. `vendor_dlkm` (`logical: true`): `/dev/block/mapper/vendor_dlkm_<slot>`. The image must not be larger
   than the existing logical partition (`blockdev --getsize64`); if it is, abort, since the app cannot
   resize partitions in `super`. Make the block device writable first (`blockdev --setrw`).
2. `vendor_boot`: `/dev/block/by-name/vendor_boot_<slot>`.
3. `boot`: `/dev/block/by-name/boot_<slot>`.
4. `sync`, reboot.

An image smaller than its physical partition is written as-is at offset 0.
