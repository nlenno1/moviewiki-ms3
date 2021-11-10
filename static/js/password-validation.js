$('document').ready (function () {
    $('#password, #password-confirm').on('keyup', function () {
        if ($('#password').val() == $('#password-confirm').val()) {
          $('#password-feedback').html('Passwords Match').css('color', '#000');
        } else 
          $('#password-feedback').html('Passwords Dont Match').css('color', 'rgb(200, 0, 0)');
    });


    $("form").submit(function(event){
        if ($('#password').val() != $('#password-confirm').val()) {
            alert('Please make sure that your passwords match');
            event.preventDefault(event);
        }
    });
})
