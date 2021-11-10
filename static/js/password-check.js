$('document').ready (function () {
    $('#password, #password-confirm').on('keyup', function () {
        if ($('#password').val() == $('#password-confirm').val()) {
          $('#password-feedback').html('Passwords Match').css('color', 'green');
        } else 
          $('#password-feedback').html('Passwords Dont Match').css('color', 'red');
    });


    $("form").submit(function(event){
        if ($('#password').val() != $('#password-confirm').val()) {
            alert('Please make sure that your passwords match');
            event.preventDefault(event);
        }
    });
})
