import datetime
import re
from pathlib import Path

import yaml

modal_html_template = """
<div id="{id}-modal" class="modal">
  <div class="modal-container">
    <div class="modal-exit">
      <a href="#"><img src="img/xbutton.svg" alt="x" width="25px" height="25px"></a>
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
</div>
"""

projbox_html_template = """
<div class="projbox {tags}">
  <p class="text">{title}</p>
  <a href="#{id}-modal"><img id={id}-projbox-img src="{projbox_img_url}" alt="{id}"></a>
</div>
"""

filter_button_template = """
<div class="tag-button">
  <button class="active" id="{tag_id}-button" value="{tag_id}" onclick="onFilterButtonPress('{tag_id}-button')">{tag}</button>
</div>
<br>
"""


def lower_case_hyphenfy(title: str) -> str:
    project_id = title.replace(" ", "-")
    project_id = project_id.lower()
    project_id = re.sub("[^a-zA-Z0-9\-\#\+]", "", project_id).lower()
    return project_id


if __name__ == "__main__":
    start_modal_marker = "<!-- Begin Modals -->"
    end_modal_marker = "<!-- End Modals -->"
    modals_html_string = f"{start_modal_marker}\n"

    start_projbox_marker = "<!-- Begin Project Boxes -->"
    end_projbox_marker = "<!-- End Project Boxes -->"
    projbox_html_string = f'{start_projbox_marker}\n<div class="projbox-container">\n'

    start_filter_button_marker = "<!-- Begin Filter Buttons -->"
    end_filter_button_marker = "<!-- End Filter Buttons -->"
    filter_button_html_string = f'{start_filter_button_marker}\n<div id="tags-sidebar">\n<div class="tag-button-container">\n'

    added_tag = {}
    projbox_html_data = []
    for file in Path("projects").glob("*/*.yaml"):
        with open(file) as f:
            project_info = yaml.safe_load(f)

        project_id = lower_case_hyphenfy(project_info["title"])
        tags_comma = ", ".join(project_info["tags"])

        modal_imgs = ""
        for img_url in project_info["modal_img_url"]:
            modal_imgs += (
                f'<img class={project_id}-modal-img src="{file.parent}/{img_url}">\n'
            )

        modal_html = modal_html_template.format(
            id=project_id,
            title=project_info["title"],
            modal_imgs=modal_imgs,
            summary=project_info["summary"],
            tags=tags_comma,
        )
        modals_html_string += f"{modal_html}"

        tag_ids_space = " ".join(
            [lower_case_hyphenfy(tag) for tag in project_info["tags"]]
        )
        date = project_info["date"]
        projbox_html_data.append(
            (
                date,
                projbox_html_template.format(
                    tags=tag_ids_space,
                    id=project_id,
                    title=project_info["title"],
                    projbox_img_url=file.parent / project_info["projbox_img_url"],
                ),
            )
        )

        for tag in project_info["tags"]:
            if tag in added_tag:
                continue
            added_tag[tag] = True

    this_website_proj_box_html = """
<div class="projbox webdev">
    <a href="index.html">
    <div id="web-proj">
        <p>This Website</p>
    </div>
    </a>
</div>
    """
    projbox_html_data.append(
        (datetime.date(2019, 1, 1), this_website_proj_box_html)
    )

    # List project boxes from most recent
    sorted_projbox_html_data = [
        projbox_html
        for _, projbox_html in sorted(
            projbox_html_data, reverse=True, key=lambda item: item[0]
        )
    ]
    for projbox_html in sorted_projbox_html_data:
        projbox_html_string += f"{projbox_html}"

    # List tags alphabetically
    for tag in sorted(added_tag.keys()):
        filter_button_html = filter_button_template.format(
            tag=tag, tag_id=lower_case_hyphenfy(tag)
        )
        filter_button_html_string += f"{filter_button_html}"

    modals_html_string += f"{end_modal_marker}"
    projbox_html_string += f"</div>\n{end_projbox_marker}"
    filter_button_html_string += f"</div>\n</div>\n{end_filter_button_marker}"

    # Find the markers in the existing html and replace content
    with open("projects.html", "r") as f:
        projects_html_str = f.read()
        projects_html_str = re.sub(
            f"{start_modal_marker}(.*?){end_modal_marker}",
            modals_html_string,
            projects_html_str,
            flags=re.DOTALL,
        )
        projects_html_str = re.sub(
            f"{start_projbox_marker}(.*?){end_projbox_marker}",
            projbox_html_string,
            projects_html_str,
            flags=re.DOTALL,
        )
        projects_html_str = re.sub(
            f"{start_filter_button_marker}(.*?){end_filter_button_marker}",
            filter_button_html_string,
            projects_html_str,
            flags=re.DOTALL,
        )

    with open("projects.html", "w") as f:
        f.write(projects_html_str)
