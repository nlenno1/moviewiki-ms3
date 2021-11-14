function dobDatePicker() {
    var year = new Date().getFullYear();
    var month = new Date().getMonth();
    var day = new Date().getDate();
    var yearsAgo = new Date(year - 8, month, day);
    var yearsAgoString = yearsAgo.toISOString().split('T')[0];
    $('#dob').attr('max', yearsAgoString);
}

function todayDatePicker() {
    var today = new Date()
    var todayString = today.toISOString().split('T')[0];
    $('input[type="date"]').attr('max', todayString);
}