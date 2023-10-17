function openInstances(tab) {
    tab.parentElement.parentElement.querySelectorAll(".active").forEach(function (e) {
        e.classList.remove("active");
    })
    tab.parentElement.classList.add("active");
    document.querySelector(".lve-details").classList.add("instances");
    document.querySelector(".lve-details").classList.remove("description");

    loadInstances();
}

function openDescription(tab) {
    tab.parentElement.parentElement.querySelectorAll(".active").forEach(function (e) {
        e.classList.remove("active");
    })
    tab.parentElement.classList.add("active");
    document.querySelector(".lve-details").classList.remove("instances");
    document.querySelector(".lve-details").classList.add("description");
}

function loadInstances() {
    // check if already loaded
    let container = document.querySelector(".lve-details #instances");
    if (container.innerText != "Loading...") {
        return;
    }
    
    window.setTimeout(function () {
        container.innerHTML = "TODO: load instance data from JSON"
    , 1000});
}