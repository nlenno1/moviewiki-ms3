$('document').ready (function () {
    $("form").submit(function(event){
        if ($('div.checkbox-group.required :checkbox:checked').length == 0) {
            alert('Please choose at least 1 "Favourite Genre"');
            event.preventDefault(event);
        }
    });
})
