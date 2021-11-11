$('document').ready (function () {
    $('#password, #password-confirm').on('keyup', function () {
        if ($('#password').val() == $('#password-confirm').val()) {
          $('#password-feedback').html('Passwords Match').css('color', '#000');
        } else 
          $('#password-feedback').html("Passwords Don't Match").css('color', 'rgb(200, 0, 0)');
    });
})
