function checkIfReviewWasMeantToBeSubmitted(event) {
    // checks for length in input value and if any over 0 then stop submit
    // all values are cleared when the section is not visible
    if($('#submit-movie-review').prop('checked') != true && ($('#review-title').val().length > 0 || $('#movie-review').val().length > 0)) {
        alert('You have entered information in the Review section but not chosen to submit it. Please correct this');
        event.preventDefault(event);
    }
}

function checkIfSeriesInformationWasMeantToBeSubmitted(event) {
    // checks for length in input value and if any over 0 then stop submit
    // all values are cleared when the section is not visible
    if ($('#submit-series-info').prop('checked') != true && ($('#series-name').val().length > 0 || $('#previous-movie-name').val().length > 0 || $('#next-movie-name').val().length > 0)) {
        alert('You have entered information in the Series Information section but not chosen to submit it. Please correct this');
        event.preventDefault(event);
    }
}

$('document').ready (function () {
    initializeSelectElementColorChange();
    initializeStarRating();
    $("form").submit(function(event){
        checkIfReviewWasMeantToBeSubmitted(event);
        checkIfSeriesInformationWasMeantToBeSubmitted(event);
        checkStarCountHasBeenEntered(event);
    });
});
