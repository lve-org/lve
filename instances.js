// prompt template (set by the template)
let PROMPT_TEMPLATE = ""
let PROMPT_PARAMETERS = []

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

function json_list(obj) {
    let s = ""
    Object.keys(obj).forEach(k => {
        if (typeof obj[k] == "string") {
            s += `${k}: "${obj[k]}"\n`
        } else {
            s += `${k}: ${obj[k]}\n`
        }
    })
    return s
}

function instance_row(instance) {
    let passed = Object.keys(instance).includes("passed") ? instance["passed"] : instance["is_safe"]
    let prompt = PROMPT_TEMPLATE;
    PROMPT_PARAMETERS.forEach(p => {
        prompt = prompt.replace(`[{${p}}|`, `[{${p}}|${instance["args"][p]}`)
    })
    let timestamp = null;
    try {
        timestamp = instance["run_info"]["timestamp"];
    } catch (e) {
        timestamp = null;
    }
    
    return `<div class='instance markdown infopanel'>
    <div class='side-by-side'>
        <div class='prompt'>
            <ul class="tabs">
                <li class="active">Chat</li>
                <!-- <li>JSON</li> -->
                <!-- <li>LMQL</li> -->
            </ul>
            <pre class='promptdown'>${prompt}[bubble:assistant|${instance["response"].trim()}]</pre>
        </div>
        <div class='metadata'>
            <label>Passed</label>
            <code class='${passed ? 'passed' : 'failed'}'>${passed}</code>
            <br/>
            <label>Recorded</label>
            ${timestamp ? `<code>${timestamp}</code>` : "<code>Unknown</code>"}
            <br/>
            <label>Parameters</label>
            <pre><code>${json_list(instance["args"])}</code></pre>
        </div>
    </div>
    <pre class='expand'><a onclick='this.parentNode.classList.toggle("expanded")'><h4>Runtime Information</h4></a><code>${JSON.stringify(instance["run_info"], null, 2)}</pre></code>
    </div>`
}

function instancesSelect(files, active) {
    let r = "<select class='instances-select' onchange='loadInstances(this.selectedIndex)'>"
    files.forEach((f, i) => {
        r += `<option value='${i}' ${i == active ? "selected" : ""}>${f.split("/").slice(-1)[0]}</option>`
    }
    )
    r += "</select>"
    return r
}

function loadInstances(index=0) {
    // check if already loaded
    let container = document.querySelector(".lve-details #instances");
    let select = INSTANCE_FILES.length > 1 ? instancesSelect(INSTANCE_FILES, index) : ""
    // let select = instancesSelect(INSTANCE_FILES)
    let file = INSTANCE_FILES[index];
    
    container.innerHTML = select + `<div class='loading'>Loading ${file}...</div>`;
    
    // load instances file as JSONL
    fetch(file).then(function (response) {
        return response.text();
    }).then(function (text) {
        let html = `<div class='instances-viewer${select != '' ? ' with-select' : ''}'>`;
        let lines = text.split("\n");
        lines.forEach(l => {
            if (l == "") {
                return;
            }
            html += instance_row(JSON.parse(l));
        })
        container.innerHTML = select + html;

        // auto promptdownify
        this.document.querySelectorAll("pre.promptdown").forEach(p => {
            pd(p)
        })
    }).catch(function (error) {
        container.innerHTML = select + `<div class='loading markdown'>Error loading ${file}:<pre><code>${error}</code></pre></div>`;
    })
}

window.addEventListener("load", function () {
    // check for #show-instances
    if (location.hash == "#show-instances") {
        openInstances(document.querySelector(".tabs #tab-instances"));
    }

    // auto promptdownify
    this.document.querySelectorAll("pre.promptdown").forEach(p => {
        pd(p)
    })
})