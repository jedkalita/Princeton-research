import math
import numpy as np
from scipy.stats import rv_discrete
import threading
import time
import logging
import random

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

class Environment: #the class that will be simulating the adversary in terms of generating rewards back and forth with
    #each player
    def __init__(self, numPlayers, N):
        self.lock = threading.Lock()
        self.numPlayers = numPlayers #no of players in the game
        self.N = N #no of strategies that each player has

    def generateRewards(self, t, strategiesPicked): #generate the cost vector for all players
    #now, we have to literally calculate all of the possible permutations between other players and their strategies
        logging.debug("About to generate rewards for time : %d" %t)

        try:
            for j in range(strategiesPicked):
                logging.debug("Player %d executed strategy %d" %j %(strategiesPicked[j]))


            totalScenarios = (self.numPlayers - 1) * N #the different scenarios of strategies per remaining players that could
            #happen
            cost = 0
            if totalScenarios == 0:
                cost = input("Single Player game. Enter cost for picked strategy above: ") #single player game
            else:
                cost = input("Enter the cost for all players: ") #prompt the user for cost against a config
        finally:
            logging.debug("Finished generating rewards for time %d" %(t))

            return cost #return the cost for all players

class Player:
    def __init__(self, T, N, env):
        self.T = T #to make the matrix
        self.N = N #the number of actions/strategies that the player has
        self.weight = np.ones((self.N), dtype=float) #each player will have their cost vector indexed acc to the time instance
        #this has been initialized to 1.0 for all, but we really only care about for t=1 for all actions acc to the
        #algorithm
        self.epsilon = math.sqrt(math.log(self.N) / self.T) #the value of learning parameter for the no regret case
        # under known T
        self.env = env #the environment object that all players will play under

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

    def changeWeight(self, pickedStrategy, t, playerID): #given cost vector at time t generated by environment/adversary,
        #change the weight of the pickedStrategy at time t for time t+1
        if t == self.T - 1: #the last time step
            return #just return
        self.weight[pickedStrategy] = self.weight[pickedStrategy] * math.pow((1 - self.epsilon),
                                                                                       self.env.generateRewards(playerID, pickedStrategy))
        #the multiplicative update formula
        print("Played ID: %d " % playerID)
        print(self.weight)

def play(players, playerID, strategiesPicked): #to play each game at each time step
    strategyPicked = players[playerID].pickStrategy() #pick the strategy
    strategiesPicked.append(strategyPicked) #for this iteration of time, per player strategy is put in a list
    #now, based upon the combination of picked strategies the same loss will be applied to each individual player

def changeWeights(players, playerID, cost_decided): #the function to change weights for each player
    # first, encode the combination of strategies
    # call an env variable that decides what this encoding yields in terms of costs for each player
    cost_per_player = env.generateRewards(strategiesPicked)
    # per player change weight
    for i in range(NumPl):
        players[i].changeWeight(cost_per_player, t, playerID)



if __name__ == '__main__':
    Tstr = input("Enter a time horizon: ")
    T = int(Tstr) #the total number of time divisions, T
    Nstr = input("Enter number of actions/strategies of user: ")
    N = int(Nstr) #total no. of actions
    NumPl = input("No. of players: ")
    NumPl = int(NumPl) #no. of players
    #initialize the environment variable
    env = Environment(NumPl, N)
    #now, initialize the players in a loop
    players = [] #the list of players
    for i in range(NumPl): #for each player
        players.append(Player(T, N, env)) #each player has been initialized

    for i in range(T): #at each time step, for each player, select an action and based on the scenario provided,
        #decide on the next action
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
            t = threading.Thread(target=changeWeights, args=(players, j, cost_decided))
            t.start()

        #now join all the threads before moving on to the next time step
        logging.debug("Waiting for all threads after finishing setting weights.")
        for t in threading.enumerate():
            if t is not main_thread:
                t.join()
        print("Moving on to time step %d" % (i + 1))

    print("Game over...")





