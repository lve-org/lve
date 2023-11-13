function initialize() {
    document.querySelectorAll('pre.promptdown').forEach(function (element) {
        element.querySelectorAll(".promptdown-var.empty").forEach(function (element) {
            // insert <input> element
            var input = document.createElement('input');
            input.type = 'text';
            input.placeholder = "Enter Value";
            element.appendChild(input);
        });
    });
}

window.addEventListener('load', initialize);