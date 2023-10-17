function copy(button) {
    // get parent code.command
    var parent = button.parentNode;
    // get first text node
    var text = parent.childNodes[0].nodeValue.trim();
    // copy to clipboard
    navigator.clipboard.writeText(text);
}