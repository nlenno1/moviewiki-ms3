function displayStarRating () {
    // retrieve average rating from html
    let maskPercentage;
    let score = document.querySelector("#average_rating").innerHTML;
    if (score > 0) { // mask percentage
        maskPercentage = 100 - (score/5)*100;
    } else {
        maskPercentage = 100;
    } // set mask width to show the correct amount of stars
    document.querySelector("#five_stars_mask").style.width = maskPercentage + "%";
}

$('document').ready (function () {
    displayStarRating ();
});

