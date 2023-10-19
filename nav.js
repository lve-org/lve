let lastToggleId = Math.random().toString(36).substring(7);
function toggleNav() {
    let toggleId = Math.random().toString(36).substring(7);
    lastToggleId = toggleId;

    if (!document.querySelector("html").classList.contains("nav-open")) {
        document.querySelector(".nav-dim").style.zIndex = 99;
    } else {
        window.setTimeout(function () {
            if (lastToggleId == toggleId)
                document.querySelector(".nav-dim").style.zIndex = -1;
        }, 200);
    }

    document.querySelector("html").classList.toggle("nav-open");
}

window.onscroll = function() {myFunction()};
function myFunction() {
  var header = document.getElementsByClassName("mobile-nav")[0];
  var sticky = header.offsetTop;

  if (window.scrollY > sticky) {
    header.classList.add("sticky");
  } else {
    header.classList.remove("sticky");
  }
}