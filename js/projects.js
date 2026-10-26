const tagButtons = [...document.querySelectorAll(".tag-button-container button")];
const resetButton = document.getElementById("reset-filters-button");
const projboxes = [...document.querySelectorAll(".projbox")];

// --- Filtering ---
// Tags are multi-select and combine as "any of". With no tags selected, everything is shown.

function applyFilter() {
    const activeTags = new Set(
        tagButtons.filter((b) => b.classList.contains("active")).map((b) => b.dataset.tag),
    );

    for (const box of projboxes) {
        const show =
            activeTags.size === 0 || box.dataset.tags.split(" ").some((tag) => activeTags.has(tag));
        box.classList.toggle("show-projbox", show);
    }

    resetButton.disabled = activeTags.size === 0;
}

document.querySelector(".tag-button-container").addEventListener("click", (evt) => {
    const button = evt.target.closest("button");
    if (!button) return;
    const active = button.classList.toggle("active");
    button.setAttribute("aria-pressed", active);
    applyFilter();
});

resetButton.addEventListener("click", () => {
    for (const button of tagButtons) {
        button.classList.remove("active");
        button.setAttribute("aria-pressed", false);
    }
    applyFilter();
});

// --- Modals ---
// A modal is a <dialog> opened by linking to its id (e.g. projects.html#twog-modal),
// so modals can be deep linked and the back button closes them.

function syncModalWithHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    const target = id ? document.getElementById(id) : null;

    for (const dialog of document.querySelectorAll("dialog[open]")) {
        if (dialog !== target) dialog.close();
    }
    if (target instanceof HTMLDialogElement && !target.open) {
        target.showModal();
    }
}

// "close" doesn't bubble, so listen in the capture phase
document.addEventListener(
    "close",
    (evt) => {
        // Drop the hash without scrolling or adding a history entry
        if (location.hash === `#${evt.target.id}`) {
            history.replaceState(null, "", location.pathname + location.search);
        }
    },
    true,
);

document.addEventListener("click", (evt) => {
    // Click on the dim area around a modal, or on its X button
    if (evt.target instanceof HTMLDialogElement) {
        evt.target.close();
    } else if (evt.target.closest("[data-close]")) {
        evt.target.closest("dialog").close();
    }
});

window.addEventListener("hashchange", syncModalWithHash);

applyFilter();
syncModalWithHash();
