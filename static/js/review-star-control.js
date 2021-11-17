$('document').ready (function () {
    initializeStarRating();
    $("form").submit(function(event){
        checkStarCountHasBeenEnteredSingleReview(event);
    });
});
