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
    def __init__(self, numPlayers, N, costs):
        self.lock = threading.Lock()
        self.numPlayers = numPlayers #no of players in the game
        self.N = N #no of strategies that each player has
        self.profits = profits  # get the cost vector per player per strategy executed for all their scenarios and store it

    def generateRewards(self, playerID, pickedStrategy): #generate the cost vector for player playerID
    # who executed strategy pickedStrategy
    #now, we have to literally calculate all of the possible permutations between other players and their strategies
        logging.debug("Waiting for a lock for player = %d" % playerID)
        self.lock.acquire()
        try:
            logging.debug("Acquired a lock for player = %d" % playerID)
            print("Player %d has executed strategy number %d" % (playerID, pickedStrategy))
            totalScenarios = (self.numPlayers - 1) * self.N #the different scenarios of strategies per remaining players
            # that could happen
            if totalScenarios == 0:
                profit = float(self.profits[pickedStrategy])
            else:
                #print(self.costs[playerID][pickedStrategy])
                for i in range(0, totalScenarios): #each scenario encoding a particular representation of opponents' strategies
                    profit = self.profits[playerID][pickedStrategy][0][i]  # prompt the user for cost against a config

        finally:
            logging.debug("Released a lock for for player = %d" % playerID)
            self.lock.release()

            return profit #this is the cost needed by player who picked the strategy

class Player:
    def __init__(self, N, env):
        self.N = N #the number of actions/strategies that the player has
        self.weight = np.ones((self.N), dtype=float) #each player will have their cost vector indexed acc to the time instance
        #this has been initialized to 1.0 for all, but we really only care about for t=1 for all actions acc to the
        #algorithm
        self.eta = 0.5  # the value of learning parameter between 0 and 1
        self.env = env #the environment object that all players will play under

        print("in the beginning....")
        print(self.weight)

    def pickStrategy(self, t): #this will be called for the t+1th time instance after the player has picked a strategy
        #acc to the weight matrix that existed at time t
        weighted_total = sum(self.weight[:])  # get the weighted sum of all strategies of the player at time t - 1
        # the above goes in the denominator
        probability = ((1 - self.eta) * (self.weight[:] / weighted_total)) + (self.eta * (1 / self.N))
        # get the probabilities for the individual weights to randomize over
        values_over = self.weight[:]  # the values over which we will pick, essentially we only need the index
        # of the strategy, hence the range() function below
        distrib = rv_discrete(values=(range(len(values_over)), probability))  # generate the distribution
        return probability, (distrib.rvs(size=1))  # pick one randomized choice from the distribution created above and return, this
        # will be the strategy that the player picks, and this index will then be changed based on the cost vector fed
        # by the environment/adversary, who will keep track of the cost of each particular strategy

    def changeWeight(self, pickedStrategy, t, playerID): #given cost vector at time t generated by environment/adversary,
        #change the weight of the pickedStrategy at time t for time t+1
        # change the weight of the pickedStrategy at time t for time t+1
        self.weight[pickedStrategy] = self.weight[pickedStrategy] * \
                                      math.exp(self.eta *
                                               ((self.env.generateRewards(playerID, pickedStrategy))
                                                / probability[pickedStrategy]) / self.N)
        print("Played ID: %d " %playerID)
        print(self.weight)
        #the multiplicative update formula

def play(players, playerID, t): #to play each game at each time step
    strategyPicked = players[playerID].pickStrategy(t) #pick the strategy
    #now, its time to change the weight of the picked strategy for the next time step by calling the environment's
    #generate rewards within, which will be operated via a lock
    players[playerID].changeWeight(strategyPicked, t, playerID)


if __name__ == '__main__':
    nof = raw_input("Enter name of file (rps/ct(.txt)) : ") #get the file depending on the game to be played that will
    #store all of the number of players/no of strategies/cost per strategy under different scenario
    fh = open(nof, 'r') #the file handler

    N = int(fh.readline())  # total no. of actions
    NumPl = int(fh.readline())  # no. of players

    scenarios = (NumPl - 1) * N #how many scenarios per picked strategy per player
    playerCosts = [] #a list that will store all the costs of a player gotten from the input file
    for i in range(NumPl): #a loop to fill up the cost per strategy per player acquired from the input file
        strategiesPerPlayer = []
        for j in range(N):
            strategiesPerPlayer.append(fh.readline().replace('\n', ''))
        playerCosts.append(strategiesPerPlayer)

    costs = np.zeros((NumPl, N, scenarios), dtype=float) #this will be the cost vector used by the
    #environment to index into the cost when a player picks a strategy
    for i in range(len(playerCosts)): #filling up the cost vector for the environment based on the list constructs
        for j in range(len(playerCosts[i])):
            curr = 0 #to iterate over how many scenarios are there to index in properly
            tmp = playerCosts[i][j].split(" ")
            for k in range(scenarios):
                costs[i][j][curr] = float(tmp[curr])
                curr = curr + 1
    if (NumPl == 1):
        costs_single = np.zeros((N), dtype = float)
        for i in range(N):
            costs_single[i] = float(playerCosts[0][i]) #get the cost vector in a different format when single player setting for ease of
        #access
        # initialize the environment variable based on whether single or multi-player
        env = Environment(NumPl, N, costs_single)
    else:
        env = Environment(NumPl, N, costs)
    #now, initialize the players in a loop
    players = [] #the list of players
    for i in range(NumPl): #for each player
        players.append(Player(N, env)) #each player has been initialized

    nextTime = True  # this will keep track of the number of time steps in which to keep playing the game
    currentTime = 1
    while (nextTime is True):  # basically at each time step each player executes a new thread of execution for picking a strategy
        # and then the process of generating rewards takes place within a lock so that only one player at any one point
        # in time is executing the environment variable for generating rewards
        for j in range(NumPl):  # for each of the players, threads will be generated individually per time step
            t = threading.Thread(target=play, args=(players, j, currentTime))
            t.start()
        # now join all the threads before moving on to the next time step
        logging.debug("Waiting for all threads.")
        main_thread = threading.currentThread()
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