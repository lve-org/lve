const COMPETITION_ENDPOINT = "http://localhost:9999"
// last input in competition widget
let FIRST_INPUT = null;
let LAST_INPUT = null;

function initialize() {
    // setup promptdown
    document.querySelectorAll('pre.promptdown').forEach(function (element) {
        element.querySelectorAll(".promptdown-var.empty").forEach(function (element) {
            // insert <input> element
            var input = document.createElement('input');
            input.type = 'text';
            input.name = "lve-parameter-" + element.querySelector(".promptdown-var-name").innerText;
            input.placeholder = "Enter Value";
            
            // check for value in local storage (key is prefixed by competition id)
            let value = localStorage.getItem(COMPETITION_ID + "-" + input.name);
            if (value) {
                input.value = value;
            }
            input.addEventListener("change", function (event) {
                localStorage.setItem(COMPETITION_ID + "-" + event.target.name, event.target.value);
            });
            
            element.appendChild(input);

            if (!FIRST_INPUT) {
                FIRST_INPUT = input;
            }
            LAST_INPUT = input;
        });
    });

    // on enter in last input, submit
    if (LAST_INPUT) {
        LAST_INPUT.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                submit();
            }
        });
    }

    // focus on first input
    if (FIRST_INPUT) {
        FIRST_INPUT.focus();
    }

    // retrieve leaderboard
    fetch(COMPETITION_ENDPOINT + "/competition/" + COMPETITION_ID + "/leaderboard")
        .then(response => response.json())
        .then(data => {
            console.log(data);
        });

    // restore highscore name from local storage if possible
    let highscoreName = localStorage.getItem("highscore-name");
    document.getElementById("highscore-name").value = highscoreName || "";
    document.getElementById("highscore-name").addEventListener("change", function (event) {
        localStorage.setItem("highscore-name", event.target.value);
    });
}

function setWidgetEnabled(state) {
    document.getElementById("competition-widget").querySelectorAll("input, button").forEach(function (element) {
        element.disabled = !state;
    });
}

function submit() {
    let payload = {}
    
    payload["user"] = document.getElementById("highscore-name").value || null;

    document.querySelectorAll('pre.promptdown input').forEach(function (element) {
        if (!element.name.startsWith("lve-parameter-")) {
            return;
        }
        let name = element.name.substring(14);
        if (Object.keys(payload).includes(name)) {
            console.warn("duplicate parameter name: " + name);
        }
        
        payload[name] = element.value;
    })

    // append to promptdown
    let output = document.getElementById("pd-output");
    pd(output, "[bubble:assistant|");

    // disable all inputs and buttons
    setWidgetEnabled(false);
    // hide all previous status messages
    document.getElementById("competition-widget").querySelectorAll(".result").forEach(function (element) {
        element.style.display = "none";
    });

    let source = new PostEventSource(COMPETITION_ENDPOINT + "/competition/" + COMPETITION_ID + "/submit", {
        method: "POST",
        cache: "no-cache",
        keepalive: true,
        headers: {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        body: JSON.stringify(payload)
    });

    source.onmessage = function (event) {
        try {
            let data = JSON.parse(event.data);
            console.log(data);
            if (data.token) {
                pd(output, output.getAttribute('pd-text') + data.token);
            } else if (data.status) {
                if (data.status == "success") {
                    document.getElementById("competition-widget").querySelector(".result.success").style.display = "block";
                    document.getElementById("competition-widget").querySelector(".result.success #score").innerText = data.score;
                } else if (data.status == "failed") {
                    document.getElementById("competition-widget").querySelector(".result.failed").style.display = "block";
                } else {
                    source.onerror("Unknown result status: " + data.status);
                }
            }
        } catch (error) {
            source.onerror("Failed to parse JSON: " + event.data);
        }
    }

    source.onerror = function (error) {
        console.log(error);
        setWidgetEnabled(true);

        if (LAST_INPUT) {
            LAST_INPUT.focus();
        }
    }

    source.onclose = function () {
        setWidgetEnabled(true);
        
        if (LAST_INPUT) {
            LAST_INPUT.focus();
        }
    }

    source.open();
}

class PostEventSource {
    constructor(url, options) {
        this.url = url;
        this.options = options;

        this.onmessage = () => {};
        this.onerror = () => {};
        this.onclose = () => {};
    }

    open() {
        let that = this;

        // use custom SSE via fetch and result streaming
        fetch(this.url, this.options)
        .then(response => response.body)
        .then(body => {
            const reader = body.getReader();
            const decoder = new TextDecoder();

            function next(value, done) {
                reader.read().then(({ value, done }) => {
                    if (done) {
                        that.onclose();
                        return;
                    }
                    let response = decoder.decode(value, { stream: true });
                    let lines = response.split("\n");
                    lines.forEach((v) => {
                        if (v.length == 0) {
                            return;
                        }
                        if (v.startsWith("data:")) {
                            that.onmessage({
                                data: v.substring(5)
                            });
                        } else {
                            console.error("malformed SSE event: ", [v]);
                        }
                    });
                    window.setTimeout(next, 0);
                })
            }
            next();
        })
        .catch(error => {
            that.onerror(error);
        });
    }
}

window.addEventListener('load', initialize);