filterSelection();

document.body.addEventListener(
    "click",
    function (evt) {
        onOutsideModalClick(evt);
    },
    false,
);

document.body.addEventListener("keydown", function (e) {
    if (e.key == "Escape") {
        exitModal();
    }
});
function toggleSidebar() {
    var buttons = document.querySelectorAll(".tag-button-container button");

    // Count number of buttons that are active
    var activeCount = 0;
    for (var i = 0; i < buttons.length; i++) {
        if (buttons[i].classList.contains("active")) {
            activeCount += 1;
        }
    }

    // Only remove all if all are active
    var removeActive = false;
    if (activeCount === buttons.length) {
        removeActive = true;
    }

    // Toggle sidebar button active
    var sidebar = document.getElementById("sidebar-toggle-button");
    if (removeActive) {
        sidebar.classList.remove("active");
    }
    else {
        sidebar.classList.add("active");
    }

    // Toggle tag buttons active
    for (var i = 0; i < buttons.length; i++) {
        if (buttons[i].classList.contains("active") && removeActive) {
            buttons[i].classList.remove("active");
        } else if (!buttons[i].classList.contains("active") && !removeActive) {
            buttons[i].classList.add("active");
        }
    }

    filterSelection();
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
    var numShow = 0;
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

        if (item.classList.contains("show-projbox")) {
            numShow += 1;
        }
    }

    var gif = document.getElementById("no-project-gif");
    if (numShow === 0) {
        gif.classList.add("show");
    }
    else if (gif.classList.contains("show")) {
        gif.classList.remove("show");
    }
}

function onOutsideModalClick(evt) {
    if (evt.target.className !== "modal" && evt.target !== document.body) {
        return;
    }

    exitModal();
}

function exitModal() {
    // Retain scroll position
    localStorage.setItem("scrollpos", window.scrollY);
    window.location.href = "#";
    var scrollpos = localStorage.getItem("scrollpos");
    if (scrollpos) window.scrollTo(0, scrollpos);
}
