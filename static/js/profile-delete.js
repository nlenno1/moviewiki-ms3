function confirm_profile_delete() {
    document.querySelector("#edit_user_profile-content").style.display = "none";
    document.querySelector("#confirm_profile_delete").style.display = "block";
    document.querySelector("#header-title").innerHTML = "Delete Account?";
}

