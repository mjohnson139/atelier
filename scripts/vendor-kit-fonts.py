"""Vendor IBM Plex Mono into the kit as TrueType files.

The kit rasterises SVG with resvg, which reads TrueType/OpenType but not WOFF2, and
must not depend on fonts installed on the machine. This script downloads the pinned
upstream npm package, checks its hash, and unwraps the complete Regular and Medium
WOFF2 files to ``kit/atelier_kit/fonts/*.ttf``. Unwrapping changes the container
only: glyphs, metrics and names are IBM's, byte for byte.

Run it only to change the vendored version (it is the one step that uses the network):

    uv run --with fonttools --with brotli scripts/vendor-kit-fonts.py
"""

import hashlib
import io
import tarfile
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont

VERSION = "2.5.0"
URL = f"https://registry.npmjs.org/@ibm/plex-mono/-/plex-mono-{VERSION}.tgz"
SHA256 = "55b5ffcfcd5e9db36ef2070b2b07a573434ca02c6f3be2b921c0b88fff29acad"
FACES = ("Regular", "Medium")

OUT = Path(__file__).resolve().parent.parent / "kit" / "atelier_kit" / "fonts"


def main() -> None:
    with urllib.request.urlopen(URL) as response:
        archive = response.read()
    digest = hashlib.sha256(archive).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"{URL}: sha256 is {digest}, expected {SHA256}")

    OUT.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        for face in FACES:
            member = tar.extractfile(f"package/fonts/complete/woff2/IBMPlexMono-{face}.woff2")
            if member is None:
                raise SystemExit(f"IBMPlexMono-{face}.woff2 is not in the package")
            # recalcTimestamp=False keeps head.modified, so the output is reproducible.
            font = TTFont(io.BytesIO(member.read()), recalcTimestamp=False)
            font.flavor = None
            target = OUT / f"IBMPlexMono-{face}.ttf"
            font.save(target)
            print(f"{target.name}  sha256 {hashlib.sha256(target.read_bytes()).hexdigest()}")

        licence = tar.extractfile("package/LICENSE.txt")
        if licence is None:
            raise SystemExit("LICENSE.txt is not in the package")
        (OUT / "OFL.txt").write_bytes(licence.read().replace(b"\r\n", b"\n"))


if __name__ == "__main__":
    main()
