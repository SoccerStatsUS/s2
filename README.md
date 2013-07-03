## A website for displaying and analyzing soccer statistics.

This is the code used to run soccerstats.us

Contains lots of useful methods and utilities, probably.



#### Deployment instructions.
1. Add to /etc/hosts, /etc/ssh_config
2. adduser chris; add chris to /etc/sudoers
3. Add ssh keys.
5. apt-get install emacs git-core
6. clone dotfiles repo
7. Go through setup.bash
8. Set up dns
9. Install mongo, leveldb (leveldb sucks; install from source)


#### Dependencies

MongoDB
*RabbitMQ

MongoDB and RabbitMQ have been installed from debs, so add to /etc/apt/sources.list:
deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen
*deb http://www.rabbitmq.com/debian/ testing main


#### Features

#### Todo

* Create a team ranking system based on the scores.


#### Bugs


#### Stats

Every game is part of several competitions. We save stats for each competition into a stats object. That should be relatively standard. 
Try to generate stats for everything that doesn't have them.

So a FC Dallas regular season  2011 game would be part of:
MLS regular season 2011, regularseasoncareer, everythingcareer, FC Dallas regular season 2011, FC Dallas regular season
National team by competition, nationalteam2011, nationalteamcareer

An FC Dallas playoff game would be part of:
MLS playofss 2011, playoffscareer, everythingcareer, FC Dallas playoffs 2011, FC Dalals playoffs

A friendly would be part of:
friendly, (that's it)

This would solve the long-lasting MLS open cup / regular season problem.

#### Soccermetrics

Difference vs ratio question about scores.

Is a 3-1 victory more like a 6-2 or a 6-4 victory?

Determines motivations of teams.

http://www.wagerlines.net/lib/etj.pdf
