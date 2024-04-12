# <div id="natures-turn-modal" class="open-modal">
#   <div class="modal-container">
#     <div class="modal-exit">
#       <a href="#"><img src="img/xbutton.svg" alt="x" width="25px" height="25px"></a>
#     </div>
#     <div class="modal-content">
#       <h2>Nature's Turn</h2>
#       <hr>
#       <img src="img/natures_turn2.png" alt="screenshot">
#       <div class="modal-text">
#         <p><b>Nature's Turn</b>
#           is our entry to the <a href="https://itch.io/jam/gmtk-2023">GMTK Game Jam 2023</a> with the theme "Reversed
#           Roles". The concept of the game is that you are
#           playing as the environment in a turn based tactics game instead of the units. Your goal is to keep peace and
#           prevent forests from destruction. The game was made over a weekend so we ended up not being able to implement
#           all the features we wanted to. You can check the game out <a
#             href="https://alghost.itch.io/natures-turn">here</a>!
#         </p>
#         <p><b>Technology</b>: Godot</p>
#       </div>
#     </div>
#   </div>
# </div>

from pathlib import Path
import yaml
import re

modal_html_template = """
<div id="{id}-modal" class="open-modal">
  <div class="modal-container">
    <div class="modal-exit">
      <a href="#"><img src="img/xbutton.svg" alt="x" width="25px" height="25px"></a>
    </div>
    <div class="modal-content">
      <h2>{title}</h2>
      <hr>
      <img src="{img_url}" alt="{img_alt}">
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

def projectidfy_title(title: str) -> str:
    project_id = title.replace(" ", "-")
    project_id = project_id.lower()
    project_id = re.sub('[^a-zA-Z0-9\-]', '', project_id).lower()
    return project_id

start_marker = "<!-- Begin Modals -->"
end_marker = "<!-- End Modals -->"
modals_html_string = f"{start_marker}\n"
for file in Path("projects").glob("*/*.yaml"):
    with open(file) as f:
        project_info = yaml.safe_load(f)

    project_id = projectidfy_title(project_info["title"])
    tags = ", ".join(project_info["tags"])
    modal_html = modal_html_template.format(id=project_id, title=project_info["title"], img_url=project_info["img_url"], img_alt=project_info["img_alt"], summary=project_info["summary"], tags=tags)
    modals_html_string += f"{modal_html}\n"
modals_html_string += f"{end_marker}\n"

with open("projects.html", "r") as f:
    projects_html_str = f.read()
    projects_html_str = re.sub(f"{start_marker}(.*?){end_marker}", modals_html_string, projects_html_str, flags=re.DOTALL)

with open("projects.html", "w") as f:
    f.write(projects_html_str)
    