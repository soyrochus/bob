
Add a login page to the application. The user should see this when they access the page

the user can login by adding username and password . Make the required changes to the Users table to support that.

It is NOT a good practice to use plain text password, however, as Bob is a development prototype, this is not a problem and helps development. Just leave a comment in the code about how this should be replaced

The Profile menu item should not be a link to a page byt rather a popup menu having menu items like: Settings, Terms & Policies and Logout. The latter should log out the user. 

Implement a safe cookie or token mechanism compatible with the server-side rendered nature of the application. 