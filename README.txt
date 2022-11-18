DATABASE URI: "postgresql://na2852:1353@34.75.94.195/proj1part2"
URL: 34.139.118.58:811
The above may change as we may not have the credits to keep our VM running until our meeting Monday, so our
project mentor told us to just have it on for our demo and afterwards.

Parts of part 1 proposal implemented or not implemented:

In our proposal, we said the user would log in via Spotify and have the ability to import their Spotify playlist data,
which we did implement. The one caveat is that we specified in our code only the first 2 playlists retrieved, 
with a limit on the number of songs, (the Spotify API orders them in the same order that they appear on your Spotify profile)
on any given download are used for the database in order to ensure the server response does not take too long. We also
said the user could filter down songs in the database by duration, assigned mood, popularity, playlist, and other traits, which
we implemented. We also said songs retrieved by filtering could be added to a New_Playlist entity that could later
be turned into a real Spotify playlist, which we implemented. We also implemented the proposed ability to submit a mood of songs to
get a set of Spotify recommendations that are added to the database.

The ability to assign a mood to tracks, albums, and artists was reduced to the ability to assign a mood to tracks and albums
because our database created in part 2 did not include a table representing that relationship set; it was already at 16 tables
when fully implemented, so we did not want to expand it further. Also, we found that our proposed functionality was more difficult
and time-consuming to implement than assumed, so we did not want to further increase
the complexity for what was essentially a duplicate of assigning a mood to tracks and albums.  

Two most interesting features:



jQuery Usage:
jQuery was used to make the sets of filtering options disappear or appear depending on which
radio button is selected. It is in index.html in a <script> tag at the bottom.