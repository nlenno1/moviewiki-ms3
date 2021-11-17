function dobDatePicker() { 
    // create date string of 8 years ago to the day
    var year = new Date().getFullYear();
    var month = new Date().getMonth();
    var day = new Date().getDate();
    var yearsAgo = new Date(year - 8, month, day);
    var yearsAgoString = yearsAgo.toISOString().split('T')[0];
    // set string as max attribute of dob date pickers
    $('#dob').attr('max', yearsAgoString);
}

function todayDatePicker() {
    // create variable containing a string of todays date
    var today = new Date();
    var todayString = today.toISOString().split('T')[0];
    // set string as max attribute for all date type date pickers
    $('input[type="date"]').attr('max', todayString);
}