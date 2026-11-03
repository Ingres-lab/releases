# Neo releases

Builds of Neo, a LineageOS-based ROM, for the POCO F4 GT / Redmi K50 Gaming (`ingres`).

Download a build from [Releases](../../releases). Each zip has a matching `.sha256` next to it.

Updates also arrive through **Settings → System → Updater**, which reads [`ingres.json`](ingres.json).

## Publishing (maintainers)

```sh
./publish.py out/target/product/ingres/lineage-24.0-<date>-UNOFFICIAL-Neo-ingres.zip --notes notes.md
```

The script copies the zip to `out/Neo-24.0-<date>-ingres.zip`, writes the `.sha256` and creates the
GitHub Release. It then prepends the entry to `ingres.json`, taking the build time, SDK level, patch
level and A/B streaming offsets from the zip's `META-INF/com/android/metadata`, and pushes.
`--dry-run` prints the commands without running them.
