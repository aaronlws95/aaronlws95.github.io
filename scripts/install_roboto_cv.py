"""Install Roboto under a private family name so the CV PDF gets a true Regular.

Run once per machine before generate_cv.py:

    python3 scripts/install_roboto_cv.py

Why this is needed
------------------
wkhtmltopdf renders through Qt, whose font matcher picks the *Medium* face
whenever one claims the requested family name. Every Roboto variant shipped on
the system (Thin, Light, Medium, Black, ...) also claims the family name
"Roboto", so asking for `font-family: Roboto` at weight 400 yields Roboto-Medium.
Body copy then renders at weight 500 against bold's 700, which flattens the
contrast between normal text, bold text and links.

Neither CSS nor fontconfig fixes it:
  * `font-weight: 400`      - ignored by the Qt matcher
  * `@font-face`            - renders a blank page on wkhtmltopdf 0.12.4
  * `font-family: "Roboto Light"` - not recognised as a family name
  * a fontconfig alias rule - no effect on the scan-time family aliases

The system font directory is root-owned, so the offending faces cannot simply be
removed. Instead this copies the four faces a CV needs into the user font
directory and rewrites their internal family name to "Roboto CV", producing a
family that contains nothing but Regular/Bold/Italic/BoldItalic. Qt then has no
Medium to choose. cv.css asks for "Roboto CV" inside its @media print block.

Nothing outside ~/.local/share/fonts is touched, and the change is undone by
deleting the RobotoCV-*.ttf files from that directory and running `fc-cache -f`.
"""

import os
import shutil
import subprocess
import sys

try:
    from fontTools.ttLib import TTFont
except ImportError:
    sys.exit("fontTools is required: pip install fonttools")

SRC_DIR = "/usr/share/fonts/googlefonts/Roboto"
DST_DIR = os.path.expanduser("~/.local/share/fonts")

NEW_FAMILY = "Roboto CV"
NEW_PS_FAMILY = "RobotoCV"

# Source filename -> subfamily. Only these four faces are installed; adding more
# weights would reintroduce the Medium-matching bug this script exists to avoid.
FACES = {
    "Roboto-Regular.ttf": "Regular",
    "Roboto-Bold.ttf": "Bold",
    "Roboto-Italic.ttf": "Italic",
    "Roboto-BoldItalic.ttf": "Bold Italic",
}

# name table IDs: 1 family, 3 unique ID, 4 full name, 6 PostScript name,
# 16 typographic family. Subfamily (2) and style (17) are left alone so the
# regular/bold/italic mapping still resolves correctly.
NAME_IDS = (1, 3, 4, 6, 16)


def main():
    if not os.path.isdir(SRC_DIR):
        sys.exit(f"Roboto not found at {SRC_DIR}")

    os.makedirs(DST_DIR, exist_ok=True)
    written = []

    for filename, style in FACES.items():
        src = os.path.join(SRC_DIR, filename)
        if not os.path.exists(src):
            print(f"skipping, not installed: {filename}")
            continue

        dst = os.path.join(DST_DIR, filename.replace("Roboto-", "RobotoCV-"))
        shutil.copyfile(src, dst)

        full = NEW_FAMILY if style == "Regular" else f"{NEW_FAMILY} {style}"
        postscript = f"{NEW_PS_FAMILY}-{style.replace(' ', '')}"

        replacements = {
            1: NEW_FAMILY,
            3: f"{postscript};{NEW_PS_FAMILY}",
            4: full,
            6: postscript,
            16: NEW_FAMILY,
        }

        font = TTFont(dst)
        for record in font["name"].names:
            if record.nameID in NAME_IDS:
                record.string = replacements[record.nameID].encode(
                    record.getEncoding()
                )
        font.save(dst)
        font.close()

        written.append(dst)
        print(f"installed {dst}  family='{NEW_FAMILY}'  style='{style}'")

    if not written:
        sys.exit("no Roboto faces were installed")

    subprocess.run(["fc-cache", "-f"], check=False, capture_output=True)
    print(f"\n--- Installed {len(written)} faces as '{NEW_FAMILY}' ---")


if __name__ == "__main__":
    main()
