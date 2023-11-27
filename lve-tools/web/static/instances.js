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

function sanitize(s, replace_square_brackets=false) {
    s = s.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    if (replace_square_brackets)
        s = s.replace("[", "\\\&#91;").replace("]", "\\\&#93;");
    return s
}


function instance_row(index, instance) {
    let passed = Object.keys(instance).includes("passed") ? instance["passed"] : instance["is_safe"]
   
    let responses = Array.isArray(instance["response"]) ? instance["response"] : [instance["response"]];
    let n = responses.length;
    let promptdown = [];
    for (let i = 0; i < n; i++) {
        let prompt = sanitize(PROMPT_TEMPLATE[i]);

        PROMPT_PARAMETERS.forEach(p => {
            prompt = prompt.replace(`[{${p}}(empty=true)|`, `[{${p}}|${instance["args"][p]}`)
        })
        
        let response = "";
        if (typeof(responses[i]) == "string") {
            response = `[bubble:assistant|${sanitize(responses[i].trim())}]`
        }
        else if (typeof(responses[i]) == "object") {
            for (const [key, value] of Object.entries(responses[i])) {
                prompt = prompt.replace(`[{${key}}(empty=true)|`, `[{${key}}|${sanitize(value, true)}`)
            }
        }
        if (n > 1) {
            promptdown.push(`<h3>Run ${i+1} of ${n}</h3>\n`)
        }
        promptdown.push(`<pre class='promptdown'>${prompt}${response}</pre>\n`)
    }
    promptdown = promptdown.join("")//"<br\\>")


    let timestamp = null;
    try {
        timestamp = instance["run_info"]["timestamp"];
    } catch (e) {
        timestamp = null;
    }

    let author = instance["author"] || "Anonymous";
    let json = JSON.stringify(instance, null, 2).replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    return `<div class='instance markdown infopanel'>
    <div class='side-by-side'>
        <div class='metadata'>
            <h1>Instance #${index}</h1>
            <label>Passed</label>
            <code class='${passed ? 'passed' : 'failed'}'>${passed}</code>
            <br/>
            <label>Recorded</label>
            ${timestamp ? `<code>${timestamp}</code>` : "<code>Unknown</code>"}
            <br/>
            <label>Author</label>
            <i class='small'>${author}</i>
            <br/>
            <label>Parameters:</label>
            <pre><code>${json_list(instance["args"])}</code></pre>
            <pre class='expand'><a onclick='this.parentNode.classList.toggle("expanded")'><h4>Full JSON</h4></a><code>${json}</pre></code>
        </div>
        <div class='prompt'>
            <ul class="tabs">
                <li class="active">Chat</li>
                <!-- <li>JSON</li> -->
                <!-- <li>LMQL</li> -->
            </ul>
            ${promptdown}
        </div>
    </div>
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
        lines.forEach((l,i) => {
            if (l == "") {
                return;
            }
            html += instance_row(i, JSON.parse(l));
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