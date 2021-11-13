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

function checkStarCountHasBeenEntered(event) {
    if ($('#star-count').val() == 0 || $('#star-count').val() == "" && $('#review-title').prop('required')) {
        alert('Please make sure that you have selected a star rating amount!');
        event.preventDefault(event);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // changes select element text color to black on change to replicate placeholder being removed
    initializeStarRating()
    $("form").submit(function(event){
        checkStarCountHasBeenEntered(event)
    });
});
