
# Remove main/

#### Todo

! Delete Salvadorean league. It's a duplicate!

Create a team ranking system based on the scores!
Soccermetrics!

Need an aliases model.

Start out with World Cup and Champions League! and EPL! and Italy!

Time to migrate to postgresql. SQLite doesn't support unique constraints.
Also, this will allow geoDjango support!

#### Bugs

Some of the main problems with this site:

1. Need a stronger scraping infrastructure.
2. Need better testing.
3. Need much better facilities for managing duplicate (players/leagues/teams/games)

5. Maybe an alias model that maps a name to a generic foreign key? Unique on the name/gfk combination.


#### Stats

So the unifying idea behind how to keep stats on the site:

Every game is part of several competitions. We save stats for each competition into a stats object. That should be relatively standard. 

So a FC Dallas regular season  2011 game would be part of:
MLS regular season 2011, regularseasoncareer, everythingcareer, FC Dallas regular season 2011, FC Dallas regular season

An FC Dallas playoff game would be part of:
MLS playofss 2011, playoffscareer, everythingcareer, FC Dallas playoffs 2011, FC Dalals playoffs

A friendly would be part of:
friendly, (that's it)

This would solve the long-lasting MLS open cup / regular season problem.

#### Competitions 

# A competition is simply a name.
# It could have some other information, like country, or format (round-robin, league)
# A start and end. (could be figured programatically)


