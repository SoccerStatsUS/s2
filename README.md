

# Deployment instructions.
1. Add to /etc/hosts, /etc/ssh_config
2. adduser chris; add chris to /etc/sudoers
3. Add ssh keys.
5. apt-get install emacs git-core
6. clone dotfiles repo
7. Go through setup.bash
8. Set up dns
9. Install mongo, leveldb (leveldb sucks; install from source)


Install: 

#### Launch

Time to launch the fucking site.

What do I need to do before releasing it?

0. Build everything.
1. Migrate to a different server.
2. add page caching.



#### Dependencies

LevelDB
RabbitMQ
MongoDB

MongoDB and RabbitMQ have been installed from debs, so add to /etc/apt/sources.list:
deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen
deb http://www.rabbitmq.com/debian/ testing main

####

Relevant standings on the date page.
Games played the same day on game detail 
next, previous game buttons
Coach, ref, attendance, city, stadium on game detail





1. create a stable server associated with a different supervisor (or no supervisor.)
2. use canvas to create some pitch stuff.

#### Todo

Create a team ranking system based on the scores.

Need an aliases model?

Migrate to postgresql. SQLite doesn't support unique constraints. Also, this will allow geoDjango support.

# Are a stat and a standing the same thing?

Each one can have:

Player, Team, Competition, Season, Nothing attached; presumably we could map goals or games played or whatever to standings.

Games maps directly to games played.

Relationship between goals, goals for?

Stats can obviously not have a player. Team Stats, League Stats, 

goals_for can represent either minutes gf or games played gf, whereas w/l/t represent only games played.

Probably need to think about the game stat (stat for one player for one game, or stat for one game or whatever. Just another kind of stat. Can just apply game to stat also...


# Homepage

Homepage should have:
1. Today's games
2. Yesterday's scores
3. Ongoing competitions (MLS, MLS Playoffs, US Open Cup, CONCACAF)


Team Detail should have recent scores graph.


#### Bugs

Some of the main problems with this site:

0. Provision AWS
1. Caching with redis.
2. Need testing.
3. Need to figure out how to distinguish players with the same name.


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

#### Competitions 

# A competition is simply a name.
# It could have some other information, like country, or format (round-robin, league)
# A start and end. (could be figured programatically)


#### Soccermetrics

# Negative binomial distribution matches number of goals scored by a team (?)
# Some people also us e poisson models though.
# 
Difference vs ratio question about scores.
Is a 3-1 victory more like a 6-2 or a 6-4 victory?
Determines motivations of teams.

http://www.wagerlines.net/lib/etj.pdf
