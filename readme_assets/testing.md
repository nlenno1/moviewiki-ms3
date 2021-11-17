# MovieWiki Testing

## Manual Testing

--- 

### User Stories

**Casual/First Time User** 
<details>
  <summary>As a Casual/First Time User, I want to be able to:</summary>

- Find out more about MovieWiki and how to use it
    - The About page, which is easily accessabily from the navbar or sidenav at all times, contains all the information needed.
- Search for specific movies or view all movies
    - On the hompage the user can search for any movies using the searchbar or they can view all movies via the Movies navbar dropdown menu
- Find the highest rateed movies and the latest releases
    - On the home page, when a user not logged in, the first movie carousel contains the top 15 highest rated movies and the second contains the 15 films with the latest release dates.
- View information about those movies
    - All information about a movie is accessible by clicking on the movie image on any movie display.
- Quickly establish if I should watch a Movie or not
    - On the movie profile page, the movie synopsis, age rating and average star rating are easy to find and therefore will help the user decide if they want to watch the movie.
    - If the user needs more information, then it is provided further down the page.
- View movie reviews including ratings
    - There is a View All Reviews button underneath the Average Star Rating on the movie's profile which allows the user to see all the movie's reviews.
    - On the view all review each review is displayed with reiew text, title, reviewr name, date of review and the star rating displayed using icons to make it more engaging.
    - The user will find the 3 latest reviews for any movie just below the movie description (if provided) on its profile.
    - If there havent been any reviews for the movies then the latest review section will not display
- Contact the admin team if I have any problems, see incorrect information or want to report anything
    - The contact page is always easliy accessible from the navbar or sidebar and it simple to complete and send.
    - When a user is logged in, the name and email fields will auto fill for ease of use.
- Create an account if I want to do more
    - The sign up page is always easliy accessible from the navbar or sidebar through the sign up button.
</details>
<br>

**Contributer** 
<details>
  <summary>As a contributer who has signed in, I want to be able to:</summary>

- Do everything a Causal User can
    - See above
- Add, edit and delete my own movie reviews
    - Add - The New Review button is in the navbar movies dropdown or the sidenav at all times, when signed in. This take the user to a form to fill out, which has clear required input markers and validation error messages if the input is not what is required.
    - Edit - On any Movie Profile the user created, the edit movie profile button is found underneath the movie logo in grey rather than gold to make it stand out from the 3 buttons above it. When this button is click, the user will be taken to the edit movie profile page, which is the same as the create movie page but with the existing values auto filled.
    - The delete review button is at the bottom of the update review page and will remove the review from the movie, the users latest reviews (if applicable) and the users reviewed movies list
- View my latest reviews and all my reviews on the site
    - A users latest reviews are displayed on thier profile page, under the "Your Latest Reviews" heading.
    - To view all a users reviews on MovieWiki, click the Viw All Review button which is either next to or underneath the "Your Latest Reviews" heading.
- Create movie profiles that don't exist yet
    - The New Movie button is in the navbar movies dropdown or the sidenav at all times, when signed in. This take the user to a form to fill out, which has clear required input markers and validation error messages if the input is not what is needed.
- Edit and delete movie profiles that I created
    - On any Movie Profile the user created, the edit movie profile button is found underneath the movie logo in grey rather than gold to make it stand out from the 3 buttons above it. 
    - When this button is click, the user will be taken to the edit movie profile page, which is the same as the create movie page but with the existing values auto filled.
    - The Delete movie button is found at the bottom of the edit movie profile form and will return the user home when the movie is deleted. 
    - Deleting a movie will remove all the reviews for that movie from the movie profile and all users profiles and will also remove the movie name from all users watched, want to watch and reviewed lists.
- Keep track of what movies I have watched, reviewed and the ones I want to watch
    - The users movies watched, want to watch and movies reviewed lists are displayed in the users profile in their own accordion sections. All movie names are links to the related movie profile page.
    - On the homepage, the 2nd movie carousel, will contain the users want to watch list movies, as long as the list is not empty. 
- Have new movies suggested to me based on my movie genre preferences, age, what I have watched and the movie's review scores
    - At the bottom of the users profile page and the first movie carousel on the home page displayes "Movies Recommended For You".
    - These movies are the top 15 in the list which is selected based on the users favourite genre list, with any films that have an age rating over the uses age removed and then sorted in by average star rating. Movies that are in the user watched list are also removed from the recommended list.
    - When viewing any movie, a movie carousel is displayed at the bottom of the page, which contains movies that share any genres with the current movie, sorted by average rating. The current movie is removed from this list.
- Edit my account information
    - The update profile button is easily found on the users profile page underneath their username.
    - This takes the user to the edit user profile form which is auto filled with the existing information to change and submit.
- Delete my account
    - The delete account button is found at the bottom of the edit user profile page.
    - When clicked the user is shown a confirmation screen which contains details about hwo their access will be effected if they delete their account.
</details>
<br>

**Admin**
<details>
  <summary>As an administrator, I want to be able to:</summary>

- Do everything a Contributer can
- Delete any Movie Profile
- Delete any Review
- Add, Modify and Delete any Genre Catagory
</details>
<br>

### Peer Review Testing

### Responsive Design & Browser Testing
Mobile Compatibility Tester - Google Mobile-Friendly Test


## Automated Testing

---

## General Testing
General Performance/SEO - Google Lighthouse

## Validation

### HTML

To validate the HTML files I used the [W3C Markup Validator](https://validator.w3.org/nu/).
I passed the url into the validator to stop any Jinja Templating Language creating errors.
For the Error page, I opened the page on a web browser, copies the HTML code and directly inputed it into the validator.

<details>
  <summary>HTML Validation Errors</summary>

Validating the HTML raised several validation errors:
|Error |Solution|
|-----|-----|
|movie image tags with an empty src attribute |add a placeholder of "none" if no movie link when creating/updating a movie document and add a function to check for "none" and replace it with a local image link if found|
|hr elements inside a ul |stop the list and start it again after the hr element in the navbar/sidebar and remove hr from navbar dropdown|
|aria-labelledby attributes of id names that didn't exist |check and update to the correct value (heading -> header)|
|textarea input elements with the pattern attribute |remove pattern attribute from textarea elements and correct error message to just length of input|
|div inside a ul for th edropdown genre lists which were targeted by a JS function |removed the div, added div classes to the ul and changed JS selector values to find ul without div|
|genre select element, for edit movie which is auto filled, which has the required attribute, needs the first option in the list to have a value equal to "" |add a first option with a value of "" and the hidden attribute |
|date input can not have a placeholder attribute |remove the placeholder attribute |
|label's for attribute must point to an Id on the page |update label's for attibute |
|id attribute can not contain whitespaces |use the jinja replace filter to replace whitespaces for dashes|
|duplicated id values for star icons |remove the id sttribute when generating the stars with Jinja|
</details>

After correcting these errors, the **HTML passed validation with no issues**. 

Below are the confirmation messages:

<details>
  <summary>HTML/Markup Validation</summary>

![Validation Image](validation/about-valid.jpg)
![Validation Image](validation/contact-valid.jpg)
![Validation Image](validation/create-movie-valid.jpg)
![Validation Image](validation/create-review-valid.jpg)
![Validation Image](validation/edit-movie-valid.jpg)
![Validation Image](validation/edit-review-valid.jpg)
![Validation Image](validation/edit-user-profile-valid.jpg)
![Validation Image](validation/genre-valid.jpg)
![Validation Image](validation/home-valid.jpg)
![Validation Image](validation/movie-search-valid.jpg)
![Validation Image](validation/profile-valid.jpg)
![Validation Image](validation/signin-valid.jpg)
![Validation Image](validation/signup-valid.jpg)
![Validation Image](validation/view-all-movies-valid.jpg)
![Validation Image](validation/view-all-user-reveiws-valid.jpg)
![Validation Image](validation/view-movie-valid.jpg)
![Validation Image](validation/view-reviews-valid.jpg)
![Validation Image](validation/error-valid.jpg)
</details>
<br>

### CSS

To validate the CSS file I used the [W3C CSS Validator](https://jigsaw.w3.org/css-validator/).
I tested the style.css by direct input.

When testing the validator found a:
- Parse Error created after using the css selector"["checkboxi]" instead of "[checkbox] i",
- Value Error created by using the font-size attribute rather than the font-weight with the value of 600,

After correcting these issues the **CSS passed validation** with 3 warnings which are about browser compatability which is why they were left.

![Validation Image](validation/css-valid-warnings.jpg)
<br>

### JavaScript

I used the [Beautify Tools JavaScript Validator](https://beautifytools.com/javascript-validator.php) to validate my JavaScript.

During validation, a few errors kept comming up which were:
1. missing semicolon
2. a variable not being defined
3. a function not being defined

I fixed all instances of error 1 and 2 however due to the way I have used the JavaScript functions, either calling them inline from the HTML or from a different JS file using event listeners, the validator can not see where the function is defined or used. 

This means the JavaScript files have the following validation errors because of how the validator works.

<details>
  <summary>JavaScript Validation Errors</summary>

Base Control

![Validation Image](validation/base-control-valid.jpg)

Create Edit Movie Validation

![Validation Image](validation/create-edit-movie-validation-valid.jpg)

Date Picker

![Validation Image](validation/date-picker-valid.jpg)

Profile Delete

![Validation Image](validation/profile-delete-valid.jpg)

Review Questions

![Validation Image](validation/review-questions-control-valid.jpg)

Review Star Function

![Validation Image](validation/review-star-function-valid.jpg)

</details>
<br>

### Python

Throughout the building of my projext, I used [flake8](https://pypi.org/project/flake8/) and [pylint](https://www.pylint.org/) installed on my IDE to validate my Python code.

When I had finished building the project, I ran one last test on [PEP8 online](http://pep8online.com/) to confirm my code is PEP8 complient. 

My app.py file **passed all PEP8 compliance validation** with no issues.

<details>
  <summary>Python Validation Results</summary>

![Validation Image](validation/python-valid.jpg)
</details>
<br>

### Colour Tester - A11y

I validated my colour scheme contrast on A11y Color Contrast Accessibility Validator to improve accessibility.

I used the Sign Up page as it contains all the colours on the site and is accessabily by a user who is not signed in.

The Sign Up page **passed** the colour contrast test with no issues.

<details>
  <summary>A11y Results</summary>

![Validation Image](validation/color-valid.jpg)
</details>