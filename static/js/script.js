const sidenavToggler = document.querySelector("#sidenav-toggler")
const sidenav = document.querySelector("#sidenav")
const closeSidenav = document.querySelector("#sidenavClose")
const contentCover = document.querySelector("#content-cover")

function openNav() {
    if (document.documentElement.clientWidth > 320) {
        sidenav.style.width = "280px";
    } else {
        sidenav.style.width = "100%";
    }
    sidenav.style.borderLeft = "5px solid #EEBC1D";
    
    contentCover.style.width = "100%";
    contentCover.style.opacity = "1";
}

function closeNav() {
    sidenav.style.width = "0";
    sidenav.style.borderLeft = "0px solid #EEBC1D";
    contentCover.style.width = "0";
    contentCover.style.opacity = "0";
}

function backToTop() {
    window.scrollTo(0, 0)
}


