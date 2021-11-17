function checkGenreHasBeenChecked(event) {
    // check that a checkbox in the dropdown has been checked
    if ($('ul.checkbox-group.required :checkbox:checked').length == 0) {
        alert('Please choose at least one Genre from the dropdown');
        event.preventDefault(event);
    }
}

$('document').ready (function () {
    $("form").submit(function(event){
        checkGenreHasBeenChecked(event);
    });
});
