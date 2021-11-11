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

function countStars () {
    stars = document.getElementsByClassName('gold-star').length;
    document.querySelector("#star-count").value =  stars
}

function initializeStarRating() {
    starList = document.getElementsByClassName('fa-star')
    for (let i = 0; i < starList.length; i++) {
        starList[i].addEventListener("click", function(){
            for (i=this.id; i < 6; i++) {
                document.getElementById(i).classList.remove("gold-star")
            }
            for (i=this.id; i > 0; i--) {
                document.getElementById(i).classList.add("gold-star")
            }
            countStars ()
        })
    }
}

function confirm_profile_delete() {
    document.querySelector("#edit_user_profile-content").style.display = "none";
    document.querySelector("#confirm_profile_delete").style.display = "block";
    document.querySelector("#header-title").innerHTML = "Delete Account?";
}

function displayStarRating () {
    score = document.querySelector("#average_review_score").innerHTML
    scorePercentage = (score/5)*100
    maskPercentage = 100 - scorePercentage
    document.querySelector("#five_stars_mask").style.width = maskPercentage + "%"
}


document.addEventListener('DOMContentLoaded', () => {
    // changes select element text color to black on change to replicate placeholder being removed
    elementList = document.getElementsByTagName('select')
    for (let i = 0; i < elementList.length; i++) {
        elementList[i].addEventListener("change", function(){
            this.classList.add("text-black");
        })
    }
    displayStarRating ()
});
