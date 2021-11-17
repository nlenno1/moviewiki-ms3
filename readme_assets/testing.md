# MovieWiki Testing

## Manual Testing

--- 

### User Stories

**Casual/First Time User** 
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


**Contributer** - As a contributer who has signed in, I want to be able to:
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

**Admin** - As an administrator, I want to be able to:
- Do everything a Contributer can
- Delete any Movie Profile
- Delete any Review
- Add, Modify and Delete any Genre Catagory


### Peer Review Testing

### Responsive Design & Browser Testing
Mobile Compatibility Tester - Google Mobile-Friendly Test


## Automated Testing

---

## General Testing
General Performance/SEO - Google Lighthouse

Colour Tester - A11y

## Validation

### HTML

To validate the HTML files I used the [W3C Markup Validator](https://validator.w3.org/nu/).
I passed the url into the validator to stop any Jinja Templating Language creating errors.
**All the HTML passed validation with no issues**. Below is the confirmation messages:

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
</details>

### CSS


### JavaScript

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

### Python

![Validation Image](validation/python-valid.jpg)