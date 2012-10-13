

"""
http://dev.soccerstats.us/media/docs/predicting-soccer-matches.pdf
A reproduction of the Monte Carlo Markov Chain prediction model described by Havard Rue and Oyvind Salvesen.

Bernoulli variable - a variable with a value of either 0 or 1 (e.g. coin flip.)
Poisson distribution - predicts the degree of spread around an average rate of occurence. e.g. given a train that arrives every ten minutes, gives the spread of wait times.

Goal model:
eA = (a,d)A -> attack and defence of team A
mu_aA, sigma^2_a,A = prior mean, variance of aA
result -> (xAB, yAB) -> xAB is the number of goals for team A



deltaAB = (aA + dA - aB -dB) / 2 -> difference in strength between teams A and B; psychological effect -> the stronger team will underestimate the strength of the weaker

assume xAB | (eA, eB) =d xAB | aA - dB - gamma * deltaAB
assume yAB | (eA, eB) =d yAB | aB - dA - gamma * deltaAB
gamma is a small constant to adjust the magnitude of the psychological effect.
in the case of games between relatively equal teams, assume gamma is positive - ie, the stronger team will underperform. This might be different if the stronger team is greatly stronger - the weaker team may give up before the game starts.

xAb and yAb should be reasonably fitted by a Poisson distribution; therefore
let c(x) and c(y) be global constants representing the average number of home and away goals
the mean team A goals should be lambda(x)AB where log lambda(x)AB = c^(x) + aA -dB - gamma*deltaAB

Something complicated about a joint probability goal model that is the conclusion of this stuff.

Time Model

let t' and t'', where t'' >= t' be two following time points where team A plays a match. We need to specify how the attack strength of A at t'' depends on t'.


Full Model

epsilon
gamma
tau


The MCMC process

Updating attack strength at aA^t''; all other variables remain constant while updating aA^t''
sample a new proposal for aA^t'' from a Gaussian distribution. sigma_q^2 is a constant variable for all all teams, attack and defense.
The new proposal is accepted with probability min{1,R} where R = ...










"""

class TeamStrength(object):

    def __init__(self, name):
        self.name = name
        self.offense = 0
        self.defense = 0




def process_games(game_list):
    team_list = [e['team1'] for e in game_list] + [e['team2'] for e in game_list] 
    teams = set(team_list)

    team_strengths = [TeamStrength(team) for team in teams]

    
    


        
