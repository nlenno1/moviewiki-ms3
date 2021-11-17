$('document').ready (function () { // after keyup event check passwords match and change css
    $('#password, #password-confirm').on('keyup', function () {
        if ($('#password').val() == $('#password-confirm').val()) {
          $('#password-feedback').html('Passwords Match').css('color', '#000');
        } else 
          $('#password-feedback').html("Passwords Don't Match").css('color', 'rgb(200, 0, 0)');
    });

    $("form").submit(function(event){ 
      // when form is submitted, provide an alert and stop the submit event if passwords don't match
      if ($('#password').val() != $('#password-confirm').val()) {
          alert('Please make sure that your passwords match');
          event.preventDefault(event);
      }
  });
});
