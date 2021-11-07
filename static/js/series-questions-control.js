$('document').ready (function () {
    console.log("jsloaded")
    // input disabled control on #series-questions section
    $("#start-series").on("click", function() {
        $("#previous-movie-container").attr('hidden', "")
        $("#next-movie-container").removeAttr('hidden')
    })
    $("#end-series").on("click", function() {
        $("#next-movie-container").attr('hidden', "")
        $("#previous-movie-container").removeAttr('hidden')
    })
    $("#middle-series").on("click", function() {
        $("#next-movie-container").removeAttr('hidden')
        $("#previous-movie-container").removeAttr('hidden')
    })
})
