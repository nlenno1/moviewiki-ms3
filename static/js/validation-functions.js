function check_star_count_has_been_entered() {
    if ($('#star-count').val() == 0 && $('#review-title').prop('required')) {
        console.log($('#star-count').val())
        alert('Please make sure that you have selected a star rating amount!');
        event.preventDefault(event);
    }
}

function check_genre_has_been_checked() {
    if ($('div.checkbox-group.required :checkbox:checked').length == 0) {
        alert('Please choose at least 1 Genre');
        event.preventDefault(event);
    }
}

function checkIfReviewWasMeantToBeSubmitted() {
    // checks for length in input value and if any over 0 then stop submit
    // all values are cleared when the section is not visible
    if($('#review-title').val().length > 0 || $('#movie-review').val().length > 0) {
        alert('You have entered information in the review section but not chosen to submit it. Please correct this');
        event.preventDefault(event);
    }
}

function checkIfSeriesInformationWasMeantToBeSubmitted() {
    // checks for length in input value and if any over 0 then stop submit
    // all values are cleared when the section is not visible
    if ($('#series-name').val().length > 0 || $('#previous-movie-name').val().length > 0 || $('#next-movie-name').val().length > 0) {
        alert('You have entered information in the Series Information section but not chosen to submit it. Please correct this');
        event.preventDefault(event);
    }
}