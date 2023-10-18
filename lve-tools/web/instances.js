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

function instance_row(instance) {
    let passed = Object.keys(instance).includes("passed") ? instance["passed"] : instance["is_safe"]
    return `<tr>
    <td class='result'>${JSON.stringify(instance["args"])}</td>
    <td class='prompt'>${JSON.stringify(instance["prompt"])}</td>    
    <td class='response'>${instance["response"]}</td>
    <td class='result'>${passed}</td>
    <td class='result'>${JSON.stringify(instance["run_info"])}</td>
    </tr>`
}

function loadInstances() {
    // check if already loaded
    let container = document.querySelector(".lve-details #instances");
    if (container.innerText != "Loading...") {
        return;
    }
    
    container.innerHTML = INSTANCE_FILES

    // load instances file as JSONL
    let file = INSTANCE_FILES[0];
    fetch(file).then(function (response) {
        return response.text();
    }).then(function (text) {
        let html = "<table class='instances-viewer'>";
        html += "<tr><th>Parameters</th><th>Prompt</th><th>Response</th><th>Passed</th><th>Run Info</th></tr>";
        let lines = text.split("\n");
        lines.forEach(l => {
            if (l == "") {
                return;
            }
            html += instance_row(JSON.parse(l));
        })
        html += "</table>";
        container.innerHTML = html;
    }).catch(function (error) {
        container.innerHTML = "Error loading instances file: " + error;
    })
}

window.addEventListener("load", function () {
    // check for #show-instances
    if (location.hash == "#show-instances") {
        openInstances(document.querySelector(".tabs #tab-instances"));
    }
})