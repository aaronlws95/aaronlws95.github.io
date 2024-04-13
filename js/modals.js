filterSelection();

document.body.addEventListener('click', function (evt) {
    onOutsideModalClick(evt);
}, false);

function toggleSidebar() {
    var sidebar = document.getElementById("tags-sidebar");
    sidebar.classList.toggle("collapsed");
    var sidebarButton = document.getElementById("sidebar-toggle-button");
    sidebarButton.classList.toggle("active");
}

function onFilterButtonPress(id) {
    // Set button to active
    var button = document.getElementById(id);

    button.classList.toggle("active");
    filterSelection();
}

function filterSelection() {
    // Get the selected categories
    var buttons = document.querySelectorAll(".tag-button-container button");
    var categories = [];
    for (var i = 0; i < buttons.length; i++) {
        if (buttons[i].classList.contains("active")) {
            categories.push(buttons[i].value);
        }
    }

    // Apply the filter
    var items = document.querySelectorAll(".projbox");
    var show = false;
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        show = false;
        for (var j = 0; j < categories.length; j++) {
            if (item.classList.contains(categories[j])) {
                show = true;
                item.classList.add("show-projbox");
                break;
            }
        }

        if (!show) {
            item.classList.remove("show-projbox");
        }
    }    
}

function onOutsideModalClick(evt) {
    if (evt.target.className !== 'modal' && evt.target !== document.body) {
        return;
    }

    // Retain scroll position
    localStorage.setItem('scrollpos', window.scrollY);
    window.location.href = "#";
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
}

