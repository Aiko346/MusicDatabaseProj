DATABASE URI: "postgresql://na2852:1353@34.75.94.195/proj1part2"
URL: 34.139.118.58:811
The above URL may change as we may not have the credits to keep our VM running until our meeting Monday, so our
project mentor told us to just have it on for our demo and afterwards.

Parts of part 1 proposal implemented or not implemented:

In our proposal, we said the user would log in via Spotify and have the ability to import their Spotify playlist data,
which we did implement. The one caveat is that we specified in our code that only the first 2 playlists retrieved (the Spotify API orders
playlists in the same order that they appear on your Spotify profile), with a limit on the number of songs, 
on any given download are used for the database in order to ensure the server response does not take too long. We
wrote the user could filter down songs in the database by duration, assigned mood, popularity, playlist, and other traits, which
we implemented. We said songs retrieved by filtering could be added to a New_Playlist entity that could later
be turned into a real Spotify playlist, which we implemented. We also implemented the proposed ability to submit a mood of songs to
get a set of Spotify recommendations that are added to the database.

The ability to assign a mood to tracks, albums, and artists was reduced to the ability to assign a mood to tracks and albums
because our database created in part 2 did not include a table representing that relationship set; it was already at 16 tables
when fully implemented, so we did not want to expand it further. Also, we found that our proposed functionality was more difficult
and time-consuming to implement than assumed, so we did not want to further increase
the complexity for what was essentially a duplicate of assigning a mood to albums.  

Two most interesting features:

One of the most interesting features is the filtering feature on the main page. SQL queries each time the main page is reloaded retrieve all
the Artists, Moods (of Albums and Tracks), Albums, Existing Playlists, Friends, and Genres that are somehow associated with your account
either through your username or by being related to your Existing Playlists (or the Recommendations Playlist created when you request recommendations
through the app). Then, the user checks which ones they want to filter by, and SQL queries are used to retrieve tracks that belong in the intersection of the 
unions of the selected options for each category - for instance, selecting "Amy" and "Bob" as Artists and "First" as an Existing Playlist
means that ultimately all tracks by Amy or Bob on First are retrieved. The SQL query that retrieves the tracks can also filter by duration and
popularity - the aforementioned query could be further reduced to all tracks by Amy or Bob on First that are less than two minutes long. 

The other most interesting feature is the ability to add Moods to Tracks and Albums. Added moods are inserted into the appropriate tables of the
database and made available for other features, allowing the user to customize their experience. Added moods are retrieved as filtering 
options via SQL, and they are used to select sets of songs via SQL that are fed to Spotify to get more recommendations. 

jQuery Usage:
jQuery was used to make the sets of filtering options disappear or appear depending on which
radio button is selected. It is in index.html in a <script> tag at the bottom.

Also, note that on startup the program asks for the cloud machine's current external IP - this is because the IP is needed 
internally for the Spotify API has to be the external IP on the cloud machine (localhost, internal IP etc. did not work). Since
it can change, we decided to ask for it as startup input to avoid literally changing the code each time we run it
or asking for it intrusively in the web front-end. 