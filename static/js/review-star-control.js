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