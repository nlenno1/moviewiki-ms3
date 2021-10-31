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

/* 
function createToastMessage (message) {
    new_toast = document.querySelector("#toast-container").append(`
    <div role="alert" aria-live="assertive" aria-atomic="true" class="toast" data-bs-autohide="false">
        <div class="toast-header">
            <strong class="me-auto">MovieWiki</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            "${message}"
        </div>
    </div>
    `)
}
*/

// processing page hide/show function
function processing() {
    document.querySelector("#content").style.display = "none";
    document.querySelector("#processing").style.display = "block";
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

    initializeStarRating()
    displayStarRating ()
    
    // input disabled control on #series-questions section
    const seriesStartCheckbox = document.querySelector("#start-series")
    const seriesEndCheckbox = document.querySelector("#end-series")
    const seriesMiddleCheckbox = document.querySelector("#middle-series")
    const previousMovie = document.querySelector("#previous-movie-name")
    const nextMovie = document.querySelector("#next-movie-name")

    seriesStartCheckbox.addEventListener ("click", function() {
        previousMovie.setAttribute('disabled', "")
        nextMovie.removeAttribute('disabled')
    })
    seriesEndCheckbox.addEventListener ("click", function() {
        previousMovie.removeAttribute('disabled')
        nextMovie.setAttribute('disabled', "")
    })
    seriesMiddleCheckbox.addEventListener ("click", function() {
        previousMovie.removeAttribute('disabled')
        nextMovie.removeAttribute('disabled')
    })
});
