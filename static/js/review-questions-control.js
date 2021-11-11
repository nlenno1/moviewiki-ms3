$('document').ready (function () {
    // input disabled control on #series-questions section  
    $("#write-review-switch").on("click", function() {
        if($('#review-title').prop('required') || $('#movie-review').prop('required') || $('#star-count').prop('required')) {
            // remove required attribute from all inputs and reset values
            $("#review-title").removeAttr('required')
            $("#movie-review").removeAttr('required')
            $("#star-count").removeAttr('required')
            $("#review-title").val('')
            $("#movie-review").val('')
            $("#star-count").val('')
            for (i=0; i < 6; i++) {
                console.log('#'+i)
                $('#'+i).removeClass("gold-star")
            }
            $("#submit-movie-review").prop('checked', false);
        } else {
            // add required value to all review inputs
            $("#review-title").attr('required', "")
            $("#movie-review").attr('required', "")
            $("#star-count").attr('required', "")
        }
    })
})
