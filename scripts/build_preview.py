"""
Turns a client preview folder (index.html + images/) into one standalone file.

    python scripts/build_preview.py <source-folder> <client-name>

writes public/preview/<client-name>.html, served at kokilsehgal.com/preview/<client-name>.
Local images are embedded in the HTML, so the page has no separate files to
break. The source folder is left unchanged; re-run this after editing it.
"""

from __future__ import annotations

import base64
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
mimetypes.add_type("image/webp", ".webp")

LOCAL_REF = re.compile(r'\b(src|href)="(?!https?:|//|/|#|data:|mailto:|tel:)([^"]+\.(?:webp|png|jpe?g|gif|svg|avif))"')
# A preload of an embedded image does nothing and would store the image twice.
LOCAL_PRELOAD = re.compile(r'<link rel="preload" as="image" href="(?!https?:|//)[^"]+"[^>]*>\r?\n?')


def main(folder: str, slug: str) -> None:
    source = (ROOT / folder).resolve()
    html = (source / "index.html").read_text(encoding="utf-8")
    html = LOCAL_PRELOAD.sub("", html)

    def embed(match: re.Match) -> str:
        attr, ref = match.groups()
        path = source / ref
        if not path.is_file():
            sys.exit(f"Missing image: {path}")
        mime = mimetypes.guess_type(path.name)[0]
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'{attr}="data:{mime};base64,{data}"'

    html, count = LOCAL_REF.subn(embed, html)

    out = ROOT / "public" / "preview" / f"{slug}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="")
    print(f"{out.relative_to(ROOT)}: {count} images embedded, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python scripts/build_preview.py <source-folder> <url-name>")
    main(sys.argv[1], sys.argv[2])
