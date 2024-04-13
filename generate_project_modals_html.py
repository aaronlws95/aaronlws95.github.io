import yaml
import re
from pathlib import Path

modal_html_template = """
<div id="{id}-modal" class="modal">
  <div class="modal-container">
    <div class="modal-content">
      <h2>{title}</h2>
      <hr>
      <img src="{modal_img_url}">
      <div class="modal-text">
        <p>
        {summary}
        </p>
        <p><b>Tags</b>: {tags}</p>
      </div>
    </div>
  </div>
</div>
"""

projbox_html_template = """
  <div class="projbox {tags}">
    <p class="text">{title}</p>
    <a href="#{id}-modal"><img src="{projbox_img_url}" alt="{id}"></a>
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
    project_id = re.sub('[^a-zA-Z0-9\-]', '', project_id).lower()
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
  for file in Path("projects").glob("*/*.yaml"):
      with open(file) as f:
          project_info = yaml.safe_load(f)

      project_id = lower_case_hyphenfy(project_info["title"])
      tags_comma = ", ".join(project_info["tags"])
      modal_html = modal_html_template.format(id=project_id, title=project_info["title"], modal_img_url=file.parent/project_info["modal_img_url"], summary=project_info["summary"], tags=tags_comma)
      modals_html_string += f"{modal_html}\n"

      tag_ids_space = " ".join([lower_case_hyphenfy(tag) for tag in project_info["tags"]])
      projbox_html = projbox_html_template.format(tags=tag_ids_space, id=project_id, title=project_info["title"], projbox_img_url=file.parent/project_info["projbox_img_url"])
      projbox_html_string += f"{projbox_html}\n"       
      
      for tag in project_info["tags"]:
        if tag in added_tag:
          continue
        added_tag[tag] = True
        filter_button_html = filter_button_template.format(tag=tag, tag_id=lower_case_hyphenfy(tag))
        filter_button_html_string += f"{filter_button_html}\n"

  modals_html_string += f"{end_modal_marker}\n"
  projbox_html_string += f"</div>\n{end_projbox_marker}\n"
  filter_button_html_string += f"</div>\n</div>\n{end_filter_button_marker}\n"

  # Find the markers in the existing html and replace content
  with open("projects.html", "r") as f:
      projects_html_str = f.read()
      projects_html_str = re.sub(f"{start_modal_marker}(.*?){end_modal_marker}", modals_html_string, projects_html_str, flags=re.DOTALL)
      projects_html_str = re.sub(f"{start_projbox_marker}(.*?){end_projbox_marker}", projbox_html_string, projects_html_str, flags=re.DOTALL)
      projects_html_str = re.sub(f"{start_filter_button_marker}(.*?){end_filter_button_marker}", filter_button_html_string, projects_html_str, flags=re.DOTALL)

  with open("projects.html", "w") as f:
      f.write(projects_html_str)
      