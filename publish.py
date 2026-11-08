#!/usr/bin/env python3
"""Publish a Neo build: GitHub Release + Updater JSON entry.

usage: publish.py <lineage-*.zip> [--org ORG] [--repo releases] --changelog FILE
                  [--prerelease] [--extra IMG ...] [--dry-run]

The Lineage Updater reads https://raw.githubusercontent.com/<org>/<repo>/main/<device>.json,
a list of builds with a "files" array. Build time, SDK level, patch level and the
A/B streaming offsets are taken from META-INF/com/android/metadata in the zip, so
the entry always matches the build (the app rejects builds whose datetime is not
newer than ro.build.date.utc or whose os_sdk_level is lower than the device's).

The changelog is copied to changelogs/<tag>.md and linked from the entry as
"changelog_url". The Updater ignores that key: NetworkUpdate and NetworkUpdateFile
are annotated @JsonIgnoreUnknownKeys.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, zipfile

def metadata(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        text = z.read("META-INF/com/android/metadata").decode()
    return dict(line.split("=", 1) for line in text.splitlines() if "=" in line)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def run(cmd, dry):
    print("+", " ".join(cmd))
    if not dry:
        subprocess.run(cmd, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip")
    ap.add_argument("--org", default=os.environ.get("NEO_GITHUB_ORG", "Ingres-lab"))
    ap.add_argument("--repo", default="releases")
    ap.add_argument("--changelog", "--notes", dest="changelog", required=True,
                    help="changelog / release notes (markdown)")
    ap.add_argument("--prerelease", action="store_true", help="mark the GitHub Release as a pre-release")
    ap.add_argument("--extra", nargs="*", default=[],
                    help="extra assets (e.g. boot.img, vendor_boot.img); a .sha256 is written for each")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    m = re.match(r"lineage-(\d+\.\d+)-(\d{8})-(\w+)-Neo-(\w+)\.zip$", os.path.basename(a.zip))
    if not m:
        sys.exit(f"unexpected zip name: {a.zip} (want lineage-<ver>-<date>-<type>-Neo-<device>.zip)")
    version, date, rtype, device = m.groups()

    md = metadata(a.zip)
    if md.get("pre-device") not in (device, None) and device not in md.get("pre-device", ""):
        sys.exit(f"zip is for {md.get('pre-device')}, not {device}")

    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "out")
    os.makedirs(out_dir, exist_ok=True)
    name = f"Neo-{version}-{date}-{device}.zip"
    dest = os.path.join(out_dir, name)
    if not os.path.exists(dest):
        shutil.copy2(a.zip, dest)
    digest = sha256(dest)
    with open(dest + ".sha256", "w") as f:
        f.write(f"{digest}  {name}\n")

    if not os.path.isfile(a.changelog):
        sys.exit(f"changelog not found: {a.changelog}")
    tag = f"{device}-{version}-{date}"
    url = f"https://github.com/{a.org}/{a.repo}/releases/download/{tag}/{name}"
    cl_rel = f"changelogs/{tag}.md"
    os.makedirs(os.path.join(here, "changelogs"), exist_ok=True)
    shutil.copyfile(a.changelog, os.path.join(here, cl_rel))
    cl_url = f"https://raw.githubusercontent.com/{a.org}/{a.repo}/main/{cl_rel}"
    entry = {
        "datetime": int(md["post-timestamp"]),
        "type": rtype.lower(),
        "version": version,
        "files": [{
            "filename": name,
            "sha256": digest,
            "size": os.path.getsize(dest),
            "url": url,
            "os_patch_level": md.get("post-security-patch-level"),
            "os_sdk_level": int(md["post-sdk-level"]),
            "ota_property_files": md.get("ota-property-files"),
        }],
        "changelog_url": cl_url,
    }

    extras = []
    for e in a.extra:
        src = os.path.abspath(e)
        edest = os.path.join(out_dir, os.path.basename(src))
        if not os.path.exists(edest):
            shutil.copy2(src, edest)
        with open(edest + ".sha256", "w") as f:
            f.write(f"{sha256(edest)}  {os.path.basename(edest)}\n")
        extras += [edest, edest + ".sha256"]

    cmd = ["gh", "release", "create", tag, dest, dest + ".sha256", *extras,
           "--repo", f"{a.org}/{a.repo}", "--title", f"Neo {version} {date} ({device})"]
    cmd += ["--notes-file", os.path.join(here, cl_rel)]
    if a.prerelease:
        cmd.append("--prerelease")
    run(cmd, a.dry_run)

    jpath = os.path.join(here, f"{device}.json")
    builds = json.load(open(jpath)) if os.path.exists(jpath) else []
    builds = [b for b in builds if b["files"][0]["filename"] != name]
    builds.insert(0, entry)
    with open(jpath, "w") as f:
        json.dump(builds, f, indent=2)
        f.write("\n")
    print(json.dumps(entry, indent=2))

    run(["git", "-C", here, "add", f"{device}.json", cl_rel], a.dry_run)
    run(["git", "-C", here, "commit", "-m", f"{device}: Neo {version} {date}"], a.dry_run)
    run(["git", "-C", here, "push"], a.dry_run)

if __name__ == "__main__":
    main()
