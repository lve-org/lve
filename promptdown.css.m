.promptdown p {
    text-indent: 2pt;
    white-space: pre-wrap;
}

.promptdown {
    font-family: monospace;
    font-size: 12pt;
    line-height: 1.5;
    background-color: white;
    padding: 10pt;
    border-radius: 5pt;
    border: 0.5pt solid rgb(204, 201, 201);

    line-height: 1.5;
    position: relative;
    
    opacity: 0.0;

    padding-right: 20pt;

    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    
    white-space: pre-wrap;
}

.promtpdown.promptdown-compiled {
    opacity: 1.0 !important;
}

html.dark .promptdown {
    background-color: #3d3d3d4c;
    color: white;
    border: 0.5pt solid rgba(64, 64, 64, 0.507);
}

.promptdown-var.cmd {
    display: none;
}

.promptdown-var {
    background-color: rgb(222, 218, 218);
    padding: 0.5pt;
    border-radius: 2pt;
    color: black;
    padding-right: 4pt;
    font-weight: 400;
    margin-right: 2pt;
    padding-left: 4pt;
}

html.dark .promptdown-var {
    color: rgb(246, 246, 246);
}

.promptdown-var.animate-immediate {
    animation: fadein 0.2s;
    animation-fill-mode: forwards;
    animation-delay: 0.0s;
}

@keyframes fadein {
    from { 
        opacity: 0; 
    }
    to { 
        opacity: 1; 
    }
}

.promptdown-var.color-none {
    background: none !important;
    padding-left: 0pt;
}

.promptdown-var .promptdown-var-name {
    color: white;
    background-color: rgba(0, 0, 0, 0.313);
    padding: 1pt;
    font-weight: bold;
    border-radius: 2pt;
    position: relative;
    top: -1.5pt;
    left: -2pt;
    font-size: 80%;
    padding: 0pt 4pt;
    font-family: monospace;
    
    margin-right: 0pt;
}

.promptdown-bubble-container.user {
    text-align: right;
}

.promptdown-bubble-container {
    margin-bottom: 8pt;
}

.faded .promptdown-bubble {
    background: transparent;
}

.hidden .promptdown-bubble {
    display: none;
}

.promptdown-bubble>.promptdown-var-name {
    display: none;
}

.promptdown-bubble {
    background-color: white;
    padding: 10pt;
    display: inline-block;
    border-radius: 5pt;
    color: black;
    max-width: 90%;

    white-space: pre-wrap;
}

html.dark .promptdown-bubble {
    color: white;
}

.promptdown-bubble.animate {
    animation: fadein-left 0.2s;
    animation-fill-mode: forwards;
    animation-delay: 0.0s;
}

@keyframes fadein-left {
    from { 
        opacity: 0; 
        transform: translateX(-20pt);
    }
    to { 
        opacity: 1; 
        transform: translateX(0px);
    }
}

.promptdown-bubble.system {
    text-align: center;
    color: grey;
    font-size: 0.85em;
    display: block;
    max-width: 100%;
    background-color: transparent;
}

.promptdown-bubble.system.animate {
    z-index: -999;
    animation: fadein-top 0.2s;
}

@keyframes fadein-top {
    from { 
        opacity: 0; 
        transform: translateY(-1pt);
    }
    to { 
        opacity: 1; 
        transform: translateY(0px);
    }
}

.promptdown-bubble.user {
    background-color: rgb(89, 122, 254);
    color: white;
    text-align: left;
}

.promptdown-bubble.user.animate {
    animation: fadein-right 0.2s;
    animation-fill-mode: forwards;
    animation-delay: 0.0s;
}

@keyframes fadein-right {
    from { 
        opacity: 0; 
        transform: translateX(20pt);
    }
    to { 
        opacity: 1; 
        transform: translateX(0px);
    }
}

.promptdown-bubble.assistant {
    color: black;
    background-color: rgb(217, 217, 217);
}

.promptdown-bubble.assistant {
    background-color: rgba(236, 233, 233, 0.873);
    /* border: 0.5pt solid rgb(217, 217, 217); */
    padding: 8pt;
}

html.dark .promptdown-bubble.assistant {
    background-color: rgba(119, 119, 119, 0.873);
    /* border: 0.5pt solid rgb(217, 217, 217); */
    padding: 8pt;
}

.promptdown h1, .promptdown h2, .promptdown h3 {
    display: block;
    margin: 0;
    padding: 0;
    font-size: 12pt;
    text-align: center;
    margin-bottom: 8pt;
}

.promptdown h1 {
    font-size: 10pt;
}

.promptdown h2 {
    font-size: 11pt;
    color: rgb(105, 105, 105);
}

.promptdown h3 {
    font-size: 10pt;
}

.promptdown-cursor {
    width: 8pt;
    background-color: rgb(196, 194, 194);
    border-radius: 2pt;
    position: relative;
    left: 2pt;
    color: transparent;
    display: inline-block;
    transform: scale(0.8);
    border: 1pt solid rgb(212, 212, 212);

    animation: blink 1s infinite;
}

.promptdown-var .promptdown-cursor {
    background-color: rgba(0, 0, 0, 0.277);
}

.promptdown-var.color-none .promptdown-cursor {
    background-color: rgb(196, 194, 194);
}

.promptdown .code_in_prompt {
    font-family: monospace;
    background-color: transparent !important;
}

@keyframes blink {
    0% {
        opacity: 0.3;
    }
    50% {
        opacity: 1;
    }
    100% {
        opacity: 0.3;
    }
}

.hidden {
    display: none;
}

.cmd-hidden {
    display: none !important;
}

.faded {
    opacity: 0.5;
    transition: opacity 0.5s;
    text-decoration: line-through;
    border-radius: 2pt;
}

.command.hidden {
    display: none;
}

/* "blue", "purple", "pink", "magenta", "red", "orange", "lightorange", "yellow", "ochre" */
.promptdown .color-blue {
    background-color: rgb(114, 140, 245);
}
html.dark .promptdown .color-blue {
    background-color: rgb(78, 96, 167);
}

.promptdown .color-purple {
    background-color: rgb(164, 142, 252);
}
html.dark .promptdown .color-purple {
    background-color: rgb(113, 92, 163);
}

.promptdown .color-pink {
    background-color: rgb(255, 120, 147);
}
html.dark .promptdown .color-pink {
    background-color: rgb(197, 92, 113);
}

.promptdown .color-magenta {
    background-color: rgb(251, 136, 251);
}
html.dark .promptdown .color-magenta {
    background-color: rgb(156, 81, 156);
}

.promptdown .color-red {
    background-color: rgb(250, 147, 147);
}
html.dark .promptdown .color-red {
    background-color: rgb(170, 86, 86);
}

.promptdown .color-orange {
    background-color: rgb(254, 122, 89);
}
html.dark .promptdown .color-orange {
    background-color: rgb(170, 86, 64);
}
.promptdown .color-lightorange {
    background-color: rgb(254, 178, 89);
}
html.dark .promptdown .color-lightorange {
    background-color: rgb(109, 87, 23);
}

.promptdown .color-yellow {
    background-color: rgb(251, 251, 192);
}

.promptdown .color-yellow {
    background-color: rgb(251, 251, 192);
}
html.dark .promptdown .color-yellow {
    background-color: rgb(107, 107, 63);
}

.promptdown .color-ochre {
    background-color: rgb(138, 188, 152);
}
html.dark .promptdown .color-ochre {
    background-color: rgb(86, 118, 96);
}

.promptdown button.promptdown-button-replay {
    position: absolute;
    top: 10pt;
    right: 10pt;
    animation: fadein 0.2s;
    color: rgb(89, 122, 254);
    font-size: 0.8em;
    border: none;
    background: transparent;
    cursor: pointer;
}

.promptdown button.promptdown-button-replay:hover {
    text-decoration: underline;
}

.promptdown button.copy {
    background-color: rgba(255, 255, 255, 0.159);
    border: 1pt solid rgba(255, 255, 255, 0.211);
    opacity: 1.0;
    
    position: absolute;
    top: 2pt;
    right: 4pt;
    left: auto;
    font-size: 10pt;
    opacity: 0.1;
    transition: opacity 0.1s;
    padding: 5pt;
    background: transparent;
}

.promptdown button.copy:hover {
    opacity: 1.0;
}
