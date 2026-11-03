#!/usr/bin/env python3
"""Publish a Neo kernel set: zip + GitHub Release + kernel/ingres.json entry.

usage: publish_kernel.py <out-dir> | --boot B --vendor-boot VB --vendor-dlkm VD
                         --profile perf|debug --changelog FILE --min-rom DATETIME_OR_VERSION
                         [--kernel-version STR] [--datetime UNIX] [--device ingres]
                         [--org Ingres-lab] [--repo releases] [--dry-run]

A kernel update is always the three images built together (the kernel and its
modules share one module ABI): boot.img, vendor_boot.img and vendor_dlkm.img.
They are packed into one zip with a manifest.json; kernel/<device>.json lists
the builds, newest first.
"""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, zipfile, zlib

IMAGES = [  # flashing order
    ("vendor_dlkm", "vendor_dlkm.img", True),
    ("vendor_boot", "vendor_boot.img", False),
    ("boot", "boot.img", False),
]
VER_RE = re.compile(rb"Linux version (\d+\.\d+\.\d+)[^\x00\n]*")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def kernel_version(boot):
    """Find the 'Linux version ...' banner in boot.img (raw, gzip or lz4 kernel)."""
    data = open(boot, "rb").read()
    m = VER_RE.search(data)
    if m:
        return m.group(0).decode(errors="replace").strip()
    i = data.find(b"\x1f\x8b\x08")
    if i >= 0:
        try:  # decompressobj tolerates the padding after the stream
            m = VER_RE.search(zlib.decompressobj(31).decompress(data[i:]))
        except zlib.error:
            m = None
        if m:
            return m.group(0).decode(errors="replace").strip()
    if shutil.which("lz4"):
        i = data.find(b"\x02\x21\x4c\x18")  # lz4 legacy frame (Image.lz4)
        if i >= 0:
            p = subprocess.run(["lz4", "-dc"], input=data[i:], capture_output=True)
            m = VER_RE.search(p.stdout)
            if m:
                return m.group(0).decode(errors="replace").strip()
    return None

def run(cmd, dry):
    print("+", " ".join(cmd))
    if not dry:
        subprocess.run(cmd, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", nargs="?", help="dir with boot.img, vendor_boot.img, vendor_dlkm.img")
    ap.add_argument("--boot"); ap.add_argument("--vendor-boot"); ap.add_argument("--vendor-dlkm")
    ap.add_argument("--profile", choices=["perf", "debug"], required=True)
    ap.add_argument("--changelog", required=True, help="markdown file")
    ap.add_argument("--min-rom", required=True,
                    help="oldest compatible ROM: unix datetime (ro.build.date.utc) or version string")
    ap.add_argument("--kernel-version", help="override the 'Linux version' banner")
    ap.add_argument("--datetime", type=int, help="build time (default: boot.img mtime)")
    ap.add_argument("--device", default="ingres")
    ap.add_argument("--org", default=os.environ.get("NEO_GITHUB_ORG", "Ingres-lab"))
    ap.add_argument("--repo", default="releases")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    paths = {}
    for part, fname, _ in IMAGES:
        p = getattr(a, part) or (os.path.join(a.out_dir, fname) if a.out_dir else None)
        if not p or not os.path.isfile(p):
            sys.exit(f"missing {fname}: {p}")
        paths[part] = p
    if not os.path.isfile(a.changelog):
        sys.exit(f"changelog not found: {a.changelog}")

    banner = a.kernel_version or kernel_version(paths["boot"])
    m = re.search(r"(\d+\.\d+\.\d+)", banner or "")
    if not m:
        sys.exit("cannot determine the kernel version; pass --kernel-version")
    base = m.group(1)

    dt = a.datetime or int(os.path.getmtime(paths["boot"]))
    day = datetime.datetime.fromtimestamp(dt, datetime.timezone.utc).strftime("%Y%m%d")
    kid = f"{base}-neo-{day}-{a.profile}"
    tag = f"{a.device}-kernel-{kid}"
    min_rom = {"datetime": int(a.min_rom)} if a.min_rom.isdigit() else {"version": a.min_rom}

    images = [{
        "partition": part,
        "filename": fname,
        "logical": logical,
        "sha256": sha256(paths[part]),
        "size": os.path.getsize(paths[part]),
    } for part, fname, logical in IMAGES]

    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "out")
    os.makedirs(out_dir, exist_ok=True)
    name = f"Neo-kernel-{kid}-{a.device}.zip"
    dest = os.path.join(out_dir, name)
    manifest = {"device": a.device, "id": kid, "kernel_version": banner, "profile": a.profile,
                "datetime": dt, "min_rom": min_rom, "images": images}
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        for part, fname, _ in IMAGES:
            z.write(paths[part], fname)
    digest = sha256(dest)
    with open(dest + ".sha256", "w") as f:
        f.write(f"{digest}  {name}\n")

    cl_rel = f"changelogs/kernel/{kid}.md"
    os.makedirs(os.path.join(here, "changelogs", "kernel"), exist_ok=True)
    shutil.copyfile(a.changelog, os.path.join(here, cl_rel))
    changelog = open(a.changelog).read()

    entry = {
        "id": kid,
        "kernel_version": banner,
        "profile": a.profile,
        "datetime": dt,
        "min_rom": min_rom,
        "download": {
            "filename": name,
            "url": f"https://github.com/{a.org}/{a.repo}/releases/download/{tag}/{name}",
            "sha256": digest,
            "size": os.path.getsize(dest),
        },
        "images": images,
        "changelog": changelog,
        "changelog_url": f"https://raw.githubusercontent.com/{a.org}/{a.repo}/main/{cl_rel}",
    }

    run(["gh", "release", "create", tag, dest, dest + ".sha256",
         "--repo", f"{a.org}/{a.repo}", "--title", f"Neo kernel {kid} ({a.device})",
         "--notes-file", os.path.join(here, cl_rel)], a.dry_run)

    jrel = f"kernel/{a.device}.json"
    jpath = os.path.join(here, jrel)
    os.makedirs(os.path.dirname(jpath), exist_ok=True)
    builds = json.load(open(jpath)) if os.path.exists(jpath) else []
    builds = [b for b in builds if b["id"] != kid]
    builds.insert(0, entry)
    with open(jpath, "w") as f:
        json.dump(builds, f, indent=2)
        f.write("\n")
    print(json.dumps(entry, indent=2))

    run(["git", "-C", here, "add", jrel, cl_rel], a.dry_run)
    run(["git", "-C", here, "commit", "-m", f"{a.device}: kernel {kid}"], a.dry_run)
    run(["git", "-C", here, "push"], a.dry_run)

if __name__ == "__main__":
    main()
