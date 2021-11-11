function displayStarRating () {
    score = document.querySelector("#average_review_score").innerHTML;
    if (score > 0) {
        scorePercentage = (score/5)*100;
        maskPercentage = 100 - scorePercentage;
    } else {
        maskPercentage = 100
    }
    document.querySelector("#five_stars_mask").style.width = maskPercentage + "%"
}

$('document').ready (function () {
    displayStarRating ()
})
