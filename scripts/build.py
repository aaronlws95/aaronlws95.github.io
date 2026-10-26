"""Build the website into dist/.

    python3 scripts/build.py [--skip-pdf]

Run from the repository root. Generating the CV PDF needs wkhtmltopdf (see README);
--skip-pdf builds without it. Nothing in dist/ is committed; CI runs this
script and deploys dist/.
"""

import hashlib
import re
import shutil
import subprocess
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml

ROOT = Path(".")
DIST = ROOT / "dist"
TEMPLATES = ROOT / "templates"

SITE_URL = "https://aaronlws95.github.io"
SOCIAL_IMAGE = "imgs/thisismyface.jpg"

# Directories copied into dist/ as-is
STATIC_DIRS = ["imgs", "js", "projects", "docs"]

# Concatenated into dist/css/style.css in this order
CSS_FILES = ["index", "general", "projects", "navbar"]

THIS_WEBSITE_DATE = date(2019, 1, 1)

PROJECT_REQUIRED_FIELDS = {
    "title": str,
    "date": date,
    "modal_img_url": list,
    "projbox_img_url": str,
    "summary": str,
    "tags": list,
}

MODAL_TEMPLATE = """
<dialog id="{id}-modal" class="modal">
  <div class="modal-container">
    <div class="modal-exit">
      <img class="modal-x-button" data-close src="imgs/xbutton.svg" alt="Close">
    </div>
    <div class="modal-content">
      <h2>{title}</h2>
      <hr>
      {modal_imgs}
      <div class="modal-text">
        {summary}
        <p><b>Tags</b>: {tags}</p>
      </div>
    </div>
  </div>
</dialog>
"""

PROJBOX_TEMPLATE = """
<div class="projbox" data-tags="{tags}">
  <p class="text">{title}</p>
  <a href="#{id}-modal"><img id="{id}-projbox-img" src="{projbox_img_url}" alt="{title}" width="250" height="250" loading="lazy"></a>
</div>
"""

THIS_WEBSITE_PROJBOX = """
<div class="projbox" data-tags="webdev">
    <a href="index.html">
    <div id="this-website">
        <p>This Website</p>
    </div>
    </a>
</div>
"""

FILTER_BUTTON_TEMPLATE = """
<div class="tag-button">
  <button type="button" aria-pressed="false" data-tag="{tag_id}">{tag}</button>
</div>
<br>
"""


class BuildError(Exception):
    pass


def render(template: str, **values: str) -> str:
    """Replace {{name}} placeholders."""
    for name, value in values.items():
        template = template.replace("{{" + name + "}}", value)
    return template


def read_template(name: str) -> str:
    return (TEMPLATES / name).read_text()


def slugify(text: str) -> str:
    """Make an id/class-safe slug, e.g. "C#" -> "csharp", "C++" -> "cpp"."""
    text = text.lower().replace("#", "sharp").replace("+", "p").replace(" ", "-")
    return re.sub(r"[^a-z0-9\-]", "", text)


def load_projects() -> list[dict]:
    projects = []
    for file in sorted(Path("projects").glob("*/*.yaml")):
        info = yaml.safe_load(file.read_text())
        for field, expected in PROJECT_REQUIRED_FIELDS.items():
            if field not in info:
                raise BuildError(f"{file}: missing field '{field}'")
            if not isinstance(info[field], expected):
                raise BuildError(
                    f"{file}: '{field}' should be {expected.__name__}, "
                    f"got {type(info[field]).__name__}"
                )
        info["dir"] = file.parent
        info["id"] = slugify(info["title"])
        projects.append(info)

    seen = {}
    for p in projects:
        if p["id"] in seen:
            raise BuildError(f"{p['dir']}: duplicate project id '{p['id']}'")
        seen[p["id"]] = p["dir"]

    tag_slugs = {}
    for p in projects:
        for tag in p["tags"]:
            other = tag_slugs.setdefault(slugify(tag), tag)
            if other != tag:
                raise BuildError(f"tags '{other}' and '{tag}' have the same slug")
    return projects


def build_projects_parts(projects: list[dict]) -> dict[str, str]:
    modals = ""
    boxes = []
    tags = set()
    for p in projects:
        modal_imgs = "".join(
            f'<img class="{p["id"]}-modal-img" src="{p["dir"]}/{img}" '
            f'alt="{p["title"]}" loading="lazy">\n'
            for img in p["modal_img_url"]
        )
        modals += MODAL_TEMPLATE.format(
            id=p["id"],
            title=p["title"],
            modal_imgs=modal_imgs,
            summary=p["summary"],
            tags=", ".join(p["tags"]),
        )
        boxes.append(
            (
                p["date"],
                PROJBOX_TEMPLATE.format(
                    tags=" ".join(slugify(t) for t in p["tags"]),
                    id=p["id"],
                    title=p["title"],
                    projbox_img_url=p["dir"] / p["projbox_img_url"],
                ),
            )
        )
        tags.update(p["tags"])
    boxes.append((THIS_WEBSITE_DATE, THIS_WEBSITE_PROJBOX))

    # Most recent first
    boxes.sort(key=lambda item: item[0], reverse=True)
    project_boxes = (
        '<div class="projbox-container">\n'
        + "".join(html for _, html in boxes)
        + "</div>\n"
    )
    filter_buttons = (
        '<div id="tags-sidebar">\n<div class="tag-button-container">\n'
        + "".join(
            FILTER_BUTTON_TEMPLATE.format(tag=t, tag_id=slugify(t))
            for t in sorted(tags)
        )
        + "</div>\n</div>\n"
    )
    return {
        "project_boxes": project_boxes,
        "filter_buttons": filter_buttons,
        "modals": modals,
    }


def versioned(path: str) -> str:
    """Append a content hash so browsers never reuse a stale cached copy."""
    digest = hashlib.sha1((DIST / path).read_bytes()).hexdigest()[:8]
    return f"{path}?v={digest}"


def build_page(
    filename: str,
    title: str,
    body: str,
    description: str,
    stylesheet: str = "css/style.css",
) -> None:
    html = render(
        read_template("base.html"),
        title=title,
        description=description,
        url=f"{SITE_URL}/{filename}",
        image=f"{SITE_URL}/{SOCIAL_IMAGE}",
        stylesheet=versioned(stylesheet),
        body=body,
    )
    (DIST / filename).write_text(html)


def build_nav(active: str) -> str:
    return render(
        read_template("nav.html"),
        home_active=' class="active"' if active == "home" else "",
        projects_active=' class="active"' if active == "projects" else "",
    )


def build_index() -> None:
    body = (
        build_nav("home")
        + "\n\n"
        + read_template("pages/index.html")
        + "\n"
        + read_template("footer.html")
    )
    build_page(
        "index.html",
        "Aaron's Home",
        body,
        description="Aaron Low's personal website. Senior robotics engineer.",
    )


def build_projects() -> None:
    parts = build_projects_parts(load_projects())
    content = render(
        read_template("pages/projects.html"),
        filter_buttons=parts["filter_buttons"],
        project_boxes=parts["project_boxes"],
    )
    body = (
        build_nav("projects")
        + "\n\n"
        + content
        + "\n"
        + read_template("footer.html")
        + "\n"
        + parts["modals"]
        + f'\n<script src="{versioned("js/projects.js")}" defer></script>'
    )
    build_page(
        "projects.html",
        "Aaron's Projects",
        body,
        description="Software, robotics, game and electronics projects by Aaron Low.",
    )


def build_cv() -> None:
    cv_html = Path("cv/cv.html").read_text()
    cv_body = re.search(r"<body>(.*?)</body>", cv_html, re.DOTALL).group(1)
    footer = (
        "<footer>\n"
        '  <a class="text" href="cv/aaronlow_cv.pdf" target="_blank" rel="noopener">download CV</a>\n'
        "</footer>"
    )
    build_page(
        "web_cv.html",
        "Aaron's CV",
        "<main>" + cv_body + "</main>" + footer,
        description="An Aaron Low CV",
        stylesheet="cv/cv.css",
    )


def build_css() -> None:
    (DIST / "css").mkdir()
    with open(DIST / "css" / "style.css", "w") as out:
        for name in CSS_FILES:
            out.write((ROOT / "css" / f"{name}.css").read_text())
            out.write("\n")


def copy_static() -> None:
    for d in STATIC_DIRS:
        shutil.copytree(ROOT / d, DIST / d)
    (DIST / "cv").mkdir()
    shutil.copy(ROOT / "cv" / "cv.css", DIST / "cv" / "cv.css")


def build_cv_pdf() -> None:
    """Render cv/cv.html to dist/cv/aaronlow_cv.pdf with wkhtmltopdf."""
    if shutil.which("wkhtmltopdf") is None:
        raise BuildError(
            "wkhtmltopdf not found (see README), or pass --skip-pdf to build without the CV PDF"
        )
    result = subprocess.run(
        [
            "wkhtmltopdf",
            "--quiet",
            "--enable-local-file-access",
            # wkhtmltopdf 0.12.x renders with screen media unless told otherwise.
            # The PDF-only rules in cv.css live in @media print, so without this
            # flag they are silently ignored.
            "--print-media-type",
            "cv/cv.html",
            str(DIST / "cv" / "aaronlow_cv.pdf"),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise BuildError(f"wkhtmltopdf failed:\n{result.stderr}")


class ReferenceCollector(HTMLParser):
    """Collects local file references and ids from an HTML document."""

    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for name in ("src", "href"):
            if name in attrs:
                self.references.append(attrs[name])


def check_references(skip: frozenset[str] = frozenset()) -> None:
    """Fail if a built page references a file or in-page id that doesn't exist."""
    problems = []
    for page in sorted(DIST.glob("*.html")):
        collector = ReferenceCollector()
        collector.feed(page.read_text())
        for ref in collector.references:
            parsed = urlparse(ref)
            if parsed.scheme or parsed.netloc:
                continue  # external (http, mailto, ...)
            if parsed.path in skip:
                continue
            if parsed.path:
                if not (DIST / unquote(parsed.path)).exists():
                    problems.append(f"{page.name}: missing file '{ref}'")
            elif parsed.fragment and parsed.fragment not in collector.ids:
                problems.append(f"{page.name}: missing id '#{parsed.fragment}'")
    if problems:
        raise BuildError("broken references:\n  " + "\n  ".join(problems))


def main() -> None:
    skip_pdf = "--skip-pdf" in sys.argv[1:]
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    copy_static()
    build_css()
    build_index()
    build_projects()
    build_cv()
    if skip_pdf:
        print("--- Skipped CV PDF (--skip-pdf); its download link will be broken ---")
    else:
        build_cv_pdf()
    check_references(skip=frozenset({"cv/aaronlow_cv.pdf"}) if skip_pdf else frozenset())
    print(f"--- Built website into {DIST}/ ---")
    print(
        f"View it with: python3 -m http.server -d {DIST}"
        "  (then open http://localhost:8000)"
    )


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        sys.exit(f"Build failed: {e}")
