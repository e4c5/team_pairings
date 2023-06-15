Zero Configuration Scrabble Pairing app
-

A scrabble pairing app that supports parralel data entry and real time updates of results online. You can start a tournament by simply specifying the number of rounds. That does not mean the tournament is not customizable. You can easily change the pairing system used, number of repeats etc through an easy to use web interface.

Audience
--
This guide is primarily for those who are familiar with python and django to set up the app on their own servers. A usage guide will be added shortly.

Getting Started
--
Clone the repo, install python requirements described in requirements.txt followed by the javascript requirements from package.json. Int the team_pair folder create a file called settings_local.py which contains your database configuration. This app uses several postgresql specific features and it's unlikely to work against other flavours of SQL.
Then do the usual manage.py migrate to create the table. Lastly before starting the server type `yarn build`. Once you start making your edits to the jsx you will have to use yarn build to make sure that the jsx is automaticaly transpiled each time you make a change.
Finaly you will need to make yourself an account with createsuperuser so that you can login. This app purposely does not include an online signup feature since tournament management should obviously be restricted to designated tournament directors.
