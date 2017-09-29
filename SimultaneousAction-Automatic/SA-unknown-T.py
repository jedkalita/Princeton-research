import math
import numpy as np
from scipy.stats import rv_discrete
import threading
import time
import logging
import random

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

def power(num):
    return math.pow(2, math.ceil(math.log(num + 1, 2)))


class Environment: #the class that will be simulating the adversary in terms of generating rewards back and forth with
    #each player
    def __init__(self, numPlayers, N, cost_scenarios):
        self.numPlayers = numPlayers #no of players in the game
        self.N = N #no of strategies that each player has
        self.cost_scenarios = cost_scenarios #the cost scenarios list

    def generateRewards(self, t, strategiesPicked): #generate the cost vector for all players
    #now, we have to literally calculate all of the possible permutations between other players and their strategies
        logging.debug("About to generate rewards for time : %d" %t)
        for j in range(len(strategiesPicked)):
            logging.debug("Player %d executed strategy %d" % (j, strategiesPicked[j]))
        totalScenarios = (self.numPlayers - 1) * self.N #the different scenarios of strategies per remaining players that could
        #happen

        #now, decode from the strategies picked which index within the cost_scenarios to get the cost from

    # now, decode from the strategies picked which index within the cost_scenarios to get the cost from
        sum = int(0)
        for i in range(self.numPlayers):
            sum = sum + (int(math.pow(self.N, i)) * strategiesPicked[i])
        print("sum is : %d" % (sum))

        cost = self.cost_scenarios[sum] #get the cost
        logging.debug("Finished generating rewards for time %d" %(t))
        return cost #return the cost for all players

class Player:
    def __init__(self, N):
        self.N = N #the number of actions/strategies that the player has
        self.weight = np.ones((self.N), dtype=float) #each player will have their cost vector indexed acc to the time instance
        #this has been initialized to 1.0 for all, but we really only care about for t=1 for all actions acc to the
        #algorithm

    def pickStrategy(self): #this will be called for the t+1th time instance after the player has picked a strategy
        #acc to the weight matrix that existed at time t
        weighted_total = sum(self.weight[:]) #get the weighted sum of all strategies of the player at time t - 1
        #the above goes in the denominator
        probability = self.weight[:] / weighted_total #get the probabilities for the individual weights to
        #randomize over
        values_over = self.weight[:] #the values over which we will pick, essentially we only need the index
        #of the strategy, hence the range() function below
        distrib = rv_discrete(values = (range(len(values_over)), probability)) #generate the distribution
        return (distrib.rvs(size = 1)) #pick one randomized choice from the distribution created above and return, this
        #will be the strategy that the player picks, and this index will then be changed based on the cost vector fed
        #by the environment/adversary, who will keep track of the cost of each particular strategy

    def changeWeight(self, cost_decided, t, strategiesPicked, playerID): #given cost vector at time t generated by environment/adversary,
        #change the weight of the pickedStrategy at time t for time t+1
        Tbar = power(t)  # find the highest higher of 2 greater than t, which is used for finding the epsilon
        epsilon = math.sqrt(math.log(self.N) / Tbar)  # the value of learning parameter for the no regret case
        # under unknown T
        logging.debug("Played ID: %d, executed strategy: %d" % (playerID, strategiesPicked[playerID]))
        self.weight[strategiesPicked[playerID]] = self.weight[strategiesPicked[playerID]] * \
                                                  math.pow((1 - epsilon), cost_decided)
        #the multiplicative update formula
        print("Player ID: %d " % playerID)
        print(self.weight)

def play(players, playerID, strategiesPicked): #to play each game at each time step
    strategyPicked = players[playerID].pickStrategy() #pick the strategy
    strategiesPicked.append(strategyPicked) #for this iteration of time, per player strategy is put in a list
    #now, based upon the combination of picked strategies the same loss will be applied to each individual player

def changeWeights(players, playerID, strategiesPicked, cost_decided, t): #the function to change weights for each player
    players[playerID].changeWeight(cost_decided, t, strategiesPicked, playerID)


if __name__ == '__main__':
    nof = raw_input("Enter name of file (rps/ct(.txt)) : ") #get the file depending on the game to be played that will
    #store all of the number of players/no of strategies/cost per strategy under different scenario
    fh = open(nof, 'r') #the file handler

    N = int(fh.readline())  # total no. of actions
    NumPl = int(fh.readline())  # no. of players

    num_costs = int(math.pow(N, NumPl)) #the total number of different cost configurations possible
    #now, read from the input file the associated costs
    cost_scenarios = []
    for i  in range(num_costs):
        cost_scenarios.append(float(fh.readline())) #read each line

    env = Environment(NumPl, N, cost_scenarios) #create the environment object
    #now, initialize the players in a loop
    players = [] #the list of players
    for i in range(NumPl): #for each player
        players.append(Player(N)) #each player has been initialized

    nextTime = True  # this will keep track of the number of time steps in which to keep playing the game
    currentTime = 1
    while (nextTime is True):  # at each time step, execute new strategy and change weights for the strategy per player
        strategiesPicked = []  # a list to hold the individual strategies picked by each player
        for j in range(NumPl):
            t = threading.Thread(target=play, args=(players, j, strategiesPicked)) #first, pick a strategy
            t.start()

        #now, close all the threads
        logging.debug("Waiting for all threads after picking strategies.")
        main_thread = threading.currentThread()
        for t in threading.enumerate():
            if t is not main_thread:
                t.join()

        #now, call the environment variable to calculate the cost based on the combination
        cost_decided = env.generateRewards(i, strategiesPicked)
        #now, after all the players have  picked an individual strategy, decide on a cost for all of them
        for j in range(NumPl):
            t = threading.Thread(target=changeWeights, args=(players, j, strategiesPicked, cost_decided, i))
            t.start()

        #now join all the threads before moving on to the next time step
        logging.debug("Waiting for all threads after finishing setting weights.")
        for t in threading.enumerate():
            if t is not main_thread:
                t.join()

        currentTime = currentTime + 1  # increment the time step by 1
        logging.debug("Moving on to time step %d" % currentTime)
        answer = raw_input("Do you want to play more? (y/n) ")
        if answer == "y":
            nextTime = True
        else:
            nextTime = False
        print("nextTime = %s" % nextTime)

    print("Game over...")
