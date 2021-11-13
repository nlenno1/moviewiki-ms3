document.addEventListener('DOMContentLoaded', () => {
    // changes select element text color to black on change to replicate placeholder being removed
    initializeStarRating()
    $("form").submit(function(event){
        checkStarCountHasBeenEnteredSingleReview(event)
    });
});

