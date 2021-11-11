// requires validation and review-star-control
$('document').ready (function () {
    $("form").submit(function(event){
        check_genre_has_been_checked()
        check_star_count_has_been_entered()
        checkIfReviewWasMeantToBeSubmitted()
        checkIfSeriesInformationWasMeantToBeSubmitted()
    });
})
