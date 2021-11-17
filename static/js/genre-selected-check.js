function checkGenreHasBeenChecked(event) {
    if ($('ul.checkbox-group.required :checkbox:checked').length == 0) {
        alert('Please choose at least one Genre from the dropdown');
        event.preventDefault(event);
    }
}

$('document').ready (function () {
    initializeSelectElementColorChange();
    $("form").submit(function(event){
        checkGenreHasBeenChecked(event);
    });
});
