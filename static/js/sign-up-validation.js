// requires validation and review-star-control
$('document').ready (function () {
    $("form").submit(function(event){
        if ($('#password').val() != $('#password-confirm').val()) {
            alert('Please make sure that your passwords match');
            event.preventDefault(event);
        }
    });
})
