document.addEventListener('DOMContentLoaded', () => {
    generateModalTableDisplay();
});

document.body.addEventListener('click', function (evt) {
    onOutsideModalClick(evt);
}, false);

function onOutsideModalClick(evt) {
    if (evt.target.className !== 'open-modal' && evt.target !== document.body) {
        return;
    }

    localStorage.setItem('scrollpos', window.scrollY);
    window.location.href = "#";
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
}

function generateModalTableDisplay() {
    var contentTable = document.getElementById("content");

    // Remove content if exists
    while (contentTable.firstChild) {
        contentTable.removeChild(contentTable.firstChild);
    }

    for (var i = 0; i < 2; i++) {
        var projrow = document.createElement("div");
        projrow.className = "projrow";
        for (var j = 0; j <= 2; j++) {
            var proj = document.createElement("div");
            proj.setAttribute("class", "proj");
            projrow.appendChild(proj);

            var title = document.createElement("p");
            title.className = "text";
            title.innerHTML = "Nature's Turn";
            proj.appendChild(title);

            var link = document.createElement("a");
            link.href = "#natures-turn-modal";
            proj.appendChild(link);

            var img = document.createElement("img");
            img.src = "img/natures_turn.png";
            img.alt = "Nature's Turn";
            link.appendChild(img);
        }
        contentTable.appendChild(projrow);
    }
}

