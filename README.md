# MovieWiki
![Live Project Representation Image]()

[Link to Live Project](https://moviewiki-project.herokuapp.com/)

---
# Introduction

This project is designed to be a space where users can share their honest reviews and opinions on movies.

This is the third of four Milestone Projects that make up the Full Stack Web Development Program at The Code Institute. The main requirements of this project are to *"build a full-stack site that allows your users to manage a common dataset about a particular domain"* using: **HTML**, **CSS**, **Javascript**, **Python+Flask** and **MongoDB**

---

# UI & UX Development Planes

# Strategy

### Project Goals
- Develop a space where users can easily find information on movies, share their opinions on various movies and find other users' reviews,
- Build a responsive app using the Mobile First design principle,
- Present any information in an aesthetically pleasing way,
- Handle any errors in such a way to help the user understand the issue and provide an easy form of contact if any error should persist,

### Business Goals
- Provide a service that Users could pay to use additional functionality in,
- Build a platform that can facillitate productive and relevant adverts or sponsored links to secondary sites (eg. Streaming services or Cinemas)

### User Demographic
- All ages and backgrounds for viewing Movie information
- Ages 8 and up for contributing
- Has an interest in movies
- Want to contribute and share their opinions
- More comfortable using mobile devices

## Value to the User
- Stores and displays information about Movies (including the next movie in the series etc)
- Provides a space to share opinions
- Helps the user keep track of movies they have watched and want to watch
- Suggests new movies that they might enjoy

### User Stories

**Casual/First Time User** - As a casual/first time user who has not created an account, I want to be able to:
- Find out more about MovieWiki and how to use it
- Search for specific movies or view all movies
- Find the highest rateed movies and the latest releases
- View information about those movies
- Quickly establish if I should watch a Movie or not
- View movie reviews including ratings
- Contact the admin team if I have any problems, see incorrect information or want to report anything
- Create an account if I want to do more

**Contributer** - As a contributer who has signed in, I want to be able to:
- Do everything a Causal User can
- Add, edit and delete my own movie reviews
- View my latest reviews and all my reviews on the site
- Create movie profiles that don't exist yet
- Edit and Delete movie profiles that I created
- Keep track of what movies I have watched, reviewed and the ones I want to watch
- Have new movies suggested to me based on my movie genre preferences, age, what I have watched and the movie's review scores
- Edit my account information
- Delete my account

**Admin** - As an administrator, I want to be able to:
- Do everything a Contributer can
- Delete any Movie Profile
- Delete any Review
- Add, Modify and Delete any Genre Catagory


# Scope
### Feature Ideas Table

After an initial planning session I drew up a list of potential features to build into this project. Below is my Importance Viability analysis of these features.

| ID      | Feature | Importance |	Viability |
| ----------- | ----------- | ----------- | ----------- |
| A | View, Create, Edit and Delete Movie Information | 5 | 5 |
| B | View, Create, Edit and Delete Movie Reviews | 5 | 5 |
| C | View, Create, Edit and Delete Movie Genre | 5 | 5 |
| D | Create, Edit and Delete Account and Log In/Out | 5 | 5 |
| E | Moderate Content being submitted by Users | 4 | 2 |
| F | Send Messages to Admin | 5 | 5 |
| G | Recieve notificatons about activity related to the User | 3 | 4 |
| H | Report/Suggest corrections/updates for Movie Profiles | 3 | 3 |
| I | Display Cinema times & location/Link to streaming services on Movie Profile | 3 | 3 |
| J | Search Movie Profiles using Name| 5 | 5 |
| K | Advanced Movie Search using mulitple parameters| 3 | 4 |
| L | View User Profile | 4 | 5 |
| M | Search User Profiles | 2 | 5 |
| N | Display Suggested/Relevant Movies to User | 4 | 5 |
| O | Tailor Movie Recommendations based on the Movie age rating | 4 | 4 |
| P | User Input Validation | 5 | 5 |
| Q | Save Movies onto a personal watched/want to watch list | 4 | 5 |
| R | Links to Socials | 3 | 5 | 

![Importance Viability Graph](readme_assets/importance_viability_chart.png)

Having performed this analysis, I decided to remove features M, K, G, H, I and E from this production release due to many factors including time limitations.
Feature R (Links to socials) has been left in due to its simplicity.
Some of these fetaures will have restricted access which will be controlled by if they are signed in or using a superuser account. 

## Functionality Requirements
- Clean and themed presentation of information
- Easy navigation to the required information
- Quick loading of the website
- Quick response times from calls to MongoDB
- Contact the developer for feedback/bug reports

## Structure

### Topology Diagrams

The Blue elements in these diagrams signify pages that are accessable from Navbar at all times.

Buttons not referances will return to the same page or return the home page.
Edit Movie Profile and Update Review only avaliable if User created page or review.
Delete functions will return to:
- Delete Review returns Movie Profile Page
- Delete Movie Returns Home
- Delete User Profile Returns Home

Guest User
![Website Topology Diagram Guest User](readme_assets/website_structure_guest.jpg)

Contributer User
![Website Topology Diagram Guest User](readme_assets/website_structure_contributer.jpg)

Admin User
![Website Topology Diagram Guest User](readme_assets/website_structure_admin.jpg)

Jinja Template Structure/Relationships
![Jinja Template Structure/Relationships](readme_assets/website_structure-jinja-template-relationships.jpg)

### Database Structure

This project uses MongoDB as its database provider. 

This diagram shows the structure and schema used in the database.
The coloured headers are the different collections and the embedded documents are shown connected to the collections.

![Database Structure Diagram](readme_assets/moviewiki_database_structure.jpeg)

## Skeleton

To view the wireframes for this project [click here](readme_assets/wireframe_display.md)

### Design Decisions

Bootstrap provides a clean user friendly appearance to the website which is easy to customise for the situation using its extensive supporting documentation.

**Colour Scheme**

I designed the colour scheme for this website from the header image that is used at the top of every page.

The colour scheme is high contrast and easily viewable. This is the final colour scheme I used:
![Colour Scheme Diagram](readme_assets/colors_diagram.png)

All navigational sections have a black (#111111) background with the contrasting yellow/gold (#FFCA18) nav links.
Mobile devices use a hamburger-menu-naigation button to access the side navbar. The sidenav is positioned on the right, to make it more accessable to mobile users using one hand.

[Sidenav Image](readme_assets/sidenav_image.png)

The forms and fields follow the same custom look consistently across the website. The base of the input is a solid black (#111111) line, which changes color if the input is not validated. The labels are grey (#929292)

**Typography**

To suit the Movie theme of the website, I chose to use [Bebas Neue](https://fonts.google.com/specimen/Bebas+Neue) for the headers, logo and some buttons.
For the rest of the text, I decieded to use the neutral looking font of [Montserrat](https://fonts.google.com/specimen/Montserrat) to balance the characted of the heading font.

**Imagery**

The header image was used to develop the colour scheme.
The movie placeholder image was chosen as it fits with the colour scheme and fonts used. 

# Features

This is a full breakdown of all the features & elements that have been be implimented for the first production release of MovieWiki.

### Multi Page Elements

**User Feedback** - All User Feedback messages will come in the form of "Flash Messages" displayed at the top of the screen, just below the header image.

**Navbar**
- Logo - to establish identity and act as a home button on smaller devices
- Home button - link to homepage
- About button - link to about page containing information, instructions and FAQs to inform users on what they can do on MovieWiki
- Movies dropdown menu which will contain links to:
    - "New Review" button - link to create review page (Only visible when logged in)
    - "New Movie" button - link to create movie page(Only visible when logged in)
    - View All Movies - link to view all movies page
- Contact button - link to contact page which will auto fill user information when logged in
- Genre button - link to genre management which will only be avaliable to superusers
- Sign In/Sign Up buttons - link to sign_in/sign_up pages (Only visable when not logged in)
- Profile button - link to user profile
- Log Out button - runs signout() function and returns to home page

At Mobile screen widths, the navbar link will be contained in a sidebar which can be toggled with a button on the navbar. The dropdown will be removed for the sidebar, and the options will be displayed in full.

**Footer**
- Logo - to establish identity and act as a home button
- Back to top button - for easier navigation of larger pages to links in the navbar
- Links to socials for promotion

### /home

- Movie displays - on load will show User appropriate or reccommended movies based on their profile and the movie's average rating
- Movie Search Bar - Will search all Movie names and return the results in the space where the Movie Displays were

### /signup

- Form input section - Collects data from user with appropriate validation. Favourite Film Genre list generated from Genre collection in the database
- Create Account button - will "POST" the data to the database and return the user to their user profile page
- Cancel button - links to homepage

### /signin

- Form input section - Collects data from user with appropriate validation
- Sign In button - compares the submitted data with the stored data to confirm Users identity. If information is correct then User is returned to their user profile page with a welcome message

### /profile

- User information section - formats and presents information recieved from the database (e.g. name, email address, favourite movie genres etc)
- Update Profile button - link to /profile/edit to edit page content
- Movies Watched/Want to Watch/Reviewed Accordion Section - Accordion section that displays all user generated lists.
- Latest Reviews Section - Shows the last 3 reviews this user added. This section will not be visible if the user has no reviews.

### /profile/edit

- Form input section - Auto filled with all existing values for the user to edit with appropriate validation
- Update Account button - updates the account information
- Delete Account button - calls the delete_profile() function and returns user to the homepage with a deletion notification (only avaliable to User who created the page)
- Cancel button - returns user to their user profile page

### /genre (admin only)

- Add New Genre input and button - Collects admin input and "POST"s it to the database
- Genre Display section - An section that will be generated from the Genre collection with an Update Genre section and Delete Genre button
- Update Genre input and button - Collects  input and "POST"s it to the database
- Delete - calls the delete_genre() function and returns to genre.html

### create_movie_profile.html

- Form input section - Collects data from user. Genre list generated from Genre collection in the database. On focus, a popover will explain what each field requires to validate the input
- "Is this movie part of a seres" switch - This switch toggles the extra input section, in and out of view, which requires additional information about the series that this movie is part of
- Create Movie Profile button - will "POST" the data to the database and return the user to the view_movie.html page they just created
- Cancel button - Cancel button will return User to home page

If user is Admin, there will also be a Delete Profile button. Delete Profile button calls the delete_profile() function and returns user to the homepage with a deletion notification.

If user is editing a Movie profile, then the buttons will be update and cancel but with similar functionality

### view_movie.html

- Movie information section - formats and presents information recieved from the database
- Latest Reviews Section - Shows basic information for the 3 latest reviews for this movie
- "I Have Watched This" Button - Toggles the movie on the Users watch list and adds the glasses icon next to the Movie Title if Movie is on the list
- "View All Reviews" button - links to view_all_movie_reviews.html to allow the user to view all the reviews of that specific Movie
- Accordion Section - Accordion elements containing supporting information, videos and possible API interfaces and monetizable links on future updates
- Edit Profile button - link to create_movie_profile.html in edit mode to edit page content (only avaliable to Admin and the User who created the page)
- Delete Profile button - calls the delete_profile() function and returns user to the homepage with a deletion notification (only avaliable to Admin and the User who created the page)
- Similar Movies Section - Displays movies in the same genre as the current film, not watched by the user and ranked in order of average star ratings

### create_review.html

- Form input section - Collects data from user. Movie title dropdown will be auto filled if coming from a Movie Profile. On focus, a popover will explain what each field requires to validate the input
- Submit Review - will "POST" the data to the database and return the user to the view_movie.html page they just created a review for
- Delete Profile button - calls the delete_profile() function and returns user to the homepage with a deletion notification
- Cancel button - Cancel button will return User to home page 

### view_all_movie_reviews

- Review cards - contain all information in the review
- Update Review button - link to create_review.html in edit mode to edit review content (only avaliable to Admin and the User who created the review)
- Delete Review button - calls the delete_profile() function and returns user to the homepage with a deletion notification (only avaliable to Admin and the User who created the review)

### contact.html

- Form input section - Collects data from user. On focus, a popover will explain what each field requires to validate the input
- Send Message Button - Passes message data onto API to send message. Returns user to contact.html with an empty form and a sent message notification.
- Cancel button - Cancel button will return User to home page 

---
## Features for future releases

- Advanced Movie Search using mulitple parameters
- Search User Profiles
- Recieve notificatons about activity related to - the User
- Display Cinema times & location/Link to streaming services on Movie Profile
- Report/Suggest corrections/updates for Movie Profiles
- Moderate Content being submitted by Users
- Actor/Actresses profiles
- Add computer location to User profile to change movie age restrictions depending on country

# Technologies Used

- [HTML5](https://developer.mozilla.org/en-US/docs/Glossary/HTML5) - Programming Language
- [CSS 3](https://developer.mozilla.org/en-US/docs/Web/CSS) - Programming Language
- [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) - Programming Language
- [MongoDB](https://www.mongodb.com/) - Data base storage
- [Flask](https://flask.palletsprojects.com/en/2.0.x/) - Python Web Framework
- [jQuery](https://jquery.com/) - JavaScript Library
- [Bootstrap v4.3.1](https://getbootstrap.com/) - Library Import
- [Google Fonts](https://fonts.google.com/) - Typography Import
- [Git Pod](https://gitpod.io/) - IDE (Integrated Development Environment)
- [Git](https://git-scm.com/) - Version Control Tool
- [Github](https://github.com/) - Cloud based hosting service to manager my Git Repositories
- [Code Institute GitPod Template](https://github.com/Code-Institute-Org/gitpod-full-template) - Provides GitPod extensions to help with code production
- [Google Chrome Development Tools](https://developer.chrome.com/docs/devtools/) - Development Tools
- [Tiny JPG](https://tinyjpg.com/) - JPG and PNG Image Compressor
- [Figma](https://www.figma.com/) - Wireframe designer software
- [HTML Formatter](https://www.freeformatter.com/html-formatter.html#ad-output) - Formatting HTML Code
- [CSS Beautifier](https://www.freeformatter.com/css-beautifier.html) - Beautifying CSS Code
- [JavaScript Validator](https://beautifytools.com/javascript-validator.php) - Validating JS code
- [GIMP](https://www.gimp.org/) - Image editor
- [Coolors](https://coolors.co/) - Colour scheme generator
- [Font Awesome](https://fontawesome.com/) - Icon provider

# Bugs and Issues

|Bug ID # | Bug      | Cause/Reason | Fix |
| ----------- | ----------- | ----------- | ----------- | 
|1 |Screen overflowing on the y axis with little or no content displayed | Set min-height attribute for content and then changed the height of other elements not in the contect div|Set all non content elements to a set height and altered the content div min-height calculation|
|2 |Variable not displaying in flash messages |Invalid F string syntax|Read up on f string documentation and improved the syntax|
|3 | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

# Testing

Testing for this project can be found in the [Testing Document](readme_assets/testing.md)

# Deployment

## Heroku Deployment

Full instructions on how to create heroku app
- connect to repo
- setup hidden/secret variables

## Database Deployment

Full instructions on how to create mongo db database
- user access
- create collections

## Repository Management

### Clone/Fork Repo

**Installing Requirements**

    pip3 install -r requirements.txt

**Setup Environmental Variables**


# Credits

errorhandlers seen in https://github.com/kairosity/mp3-snapathon/
readme structure.components https://github.com/RussOakham/wanderlust-recipes/

### Code snippets

### Resources

## Content

## Media 
**Images**
- Header image from [PIXABAY](https://pixabay.com/photos/movie-film-roll-filmstrip-analog-3057394/)
- Favicon from [PNGEGG](https://www.pngegg.com/en/png-zwxhn)
- Fovie placeholder from [PNGAAA](https://www.pngaaa.com/detail/3488028)

## Acknowledgments

README template used to produce this documentation is from [Code Institute README Template](https://github.com/Code-Institute-Solutions/readme-template)
