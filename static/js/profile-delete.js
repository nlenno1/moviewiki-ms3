function confirmProfileDelete() {
    // remove all content and replace it with a confirmation notice
    document.querySelector("#edit_user_profile-content").style.display = "none";
    document.querySelector("#confirm_profile_delete").style.display = "block";
    document.querySelector("#header-title").innerHTML = "Delete Account?";
}

