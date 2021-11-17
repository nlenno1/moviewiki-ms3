function countStars () { // count the gold stars and set it to the star count value
    let stars = document.getElementsByClassName('gold-star').length;
    document.querySelector("#star-count").value =  stars;
}

function initializeStarRating() { // fin the star icons on the page
    let starList = document.getElementsByClassName('fa-star');
    for (let i = 0; i < starList.length; i++) {
        starList[i].addEventListener("click", function(){ // stars have id of 1 to 5
            for (let i=this.id; i < 6; i++) { // all stars above the star clicked are turned black
                document.getElementById(i).classList.remove("gold-star");
            } // star clicked and all stars below are turned gold
            for (let i=this.id; i > 0; i--) {
                document.getElementById(i).classList.add("gold-star");
            } // set star-count value if not pass in from python
            countStars();
        });
    }
}

function checkStarCountHasBeenEntered(event) {
    if (($('#star-count').val() == 0 || $('#star-count').val() == "") && $('#review-title').prop('required')) {
        alert('Please make sure that you have selected a star rating amount!');
        event.preventDefault(event);
    }
}

function checkStarCountHasBeenEnteredSingleReview(event) {
    if ($('#star-count').val() == 0 || $('#star-count').val() == "") {
        alert('Please make sure that you have selected a star rating amount!');
        event.preventDefault(event);
    }
}