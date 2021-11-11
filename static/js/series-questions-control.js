$('document').ready (function () {
    // input disabled control on #series-questions section
    $("#start-series").on("click", function() {
        //remove previous movie
        $("#previous-movie-container").attr('hidden', "")
        $("#next-movie-name").removeAttr('required')
        $("#previous-movie-name").val("");
        // add next movie and make it required
        $("#next-movie-container").removeAttr('hidden')
        $("#next-movie-name").attr('required', "")

    })
    $("#end-series").on("click", function() {
        // remove next movie
        $("#next-movie-container").attr('hidden', "")
        $("#previous-movie-name").removeAttr('required')
        $("#next-movie-name").val("");
        // add previous movie and make required
        $("#previous-movie-container").removeAttr('hidden')
        $("#previous-movie-name").attr('required', "")

    })
    $("#middle-series").on("click", function() {
        // make both inputs visable and required
        $("#next-movie-container").removeAttr('hidden')
        $("#next-movie-name").attr('required', "")
        $("#previous-movie-container").removeAttr('hidden')
        $("#previous-movie-name").attr('required', "")
    })
    $("#series-switch").on("click", function() {
        if($('#series-name').prop('required')) {
            // reset series form
            $("#series-name").removeAttr('required')
            $("#previous-movie-name").removeAttr('required')
            $("#next-movie-name").removeAttr('required')
            $("#start-series").removeAttr('required')
            $("#start-series").prop('checked', false);
            $("#middle-series").prop('checked', false);
            $("#end-series").prop('checked', false);
            $("#submit-series-info").prop('checked', false);
            $("#series-name").val("");
            $("#next-movie-name").val("");
            $("#previous-movie-name").val("");
            $("#next-movie-container").attr('hidden', "")
            $("#previous-movie-container").attr('hidden', "")
        } else {
            $("#series-name").attr('required', "")
            $("#start-series").attr('required', "")
        }
    })
})
