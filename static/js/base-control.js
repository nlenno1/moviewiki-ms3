let contentCover = document.getElementById("content-cover");
let sidenav = document.getElementById("sidenav");

function openNav() {
    // check screensize and set width of sidenav with border
    if (document.documentElement.clientWidth > 320) {
        sidenav.style.width = "280px";
    } else {
        sidenav.style.width = "100%";
    }
    sidenav.style.borderLeft = "5px solid #EEBC1D";
    // add content cover over the rest of the page
    contentCover.style.width = "100%";
    contentCover.style.opacity = "1";
}

function closeNav() {
    // remove sidenav width and border
    sidenav.style.width = "0";
    sidenav.style.borderLeft = "0px solid #EEBC1D";
    // remove content cover
    contentCover.style.width = "0";
    contentCover.style.opacity = "0";
}

function backToTop() {
    //scroll window to the top of the page
    window.scrollTo(0, 0);
}
