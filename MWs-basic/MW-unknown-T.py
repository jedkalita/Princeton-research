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
    def __init__(self, numPlayers, N):
        self.lock = threading.Lock()
        self.numPlayers = numPlayers #no of players in the game
        self.N = N #no of strategies that each player has

    def generateRewards(self, playerID, pickedStrategy): #generate the cost vector for player playerID
    # who executed strategy pickedStrategy
    #now, we have to literally calculate all of the possible permutations between other players and their strategies
        logging.debug("Waiting for a lock for player = %d" % playerID)
        self.lock.acquire()
        try:
            logging.debug("Acquired a lock for player = %d" % playerID)
            print("Player %d has executed strategy number %d" % (playerID, pickedStrategy))
            totalScenarios = (self.numPlayers - 1) * N #the different scenarios of strategies per remaining players that could
            #happen
            expectedCost = 0
            if totalScenarios == 0:
                expectedCost = input("Single Player game. Enter cost for picked strategy above: ")
            else:
                for i in range(0, totalScenarios): #each scenario encoding a particular representation of opponents' strategies
                    cost = input("Enter the cost for scenario %d: " % (i + 1)) #prompt the user for cost against a config
                    expectedCost = expectedCost + cost #keep the sum count
                expectedCost = (expectedCost * 1.0) / (totalScenarios * 1.0) #to get the expectation
        finally:
            logging.debug("Released a lock for for player = %d" % playerID)
            self.lock.release()
            return expectedCost #this is the cost needed by player who picked the strategy

class Player:
    def __init__(self, N, env):
        self.N = N #the number of actions/strategies that the player has
        self.weight = np.ones((self.N), dtype=float) #each player will have their cost vector indexed acc to the time instance
        #this has been initialized to 1.0 for all, but we really only care about for t=1 for all actions acc to the
        #algorithm
        self.env = env #the environment object that all players will play under

    def pickStrategy(self, t): #this will be called for the t+1th time instance after the player has picked a strategy
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
        Tbar = power(t) #find the highest higher of 2 greater than t, which is used for finding the epsilon
        epsilon = math.sqrt(math.log(self.N) / Tbar) #the value of learning parameter for the no regret case
        # under unknown T
        self.weight[pickedStrategy] = self.weight[pickedStrategy] * math.pow((1 - epsilon),
                                                                                       self.env.generateRewards(playerID, pickedStrategy))
        #the multiplicative update formula
        print("Played ID: %d " % playerID)
        print(self.weight)

def play(players, playerID, t): #to play each game at each time step
    strategyPicked = players[playerID].pickStrategy(t) #pick the strategy
    #now, its time to change the weight of the picked strategy for the next time step by calling the environment's
    #generate rewards within, which will be operated via a lock
    players[playerID].changeWeight(strategyPicked, t, playerID)


if __name__ == '__main__':
    Nstr = input("Enter number of actions/strategies of user: ")
    N = int(Nstr) #total no. of actions
    NumPl = input("No. of players: ")
    NumPl = int(NumPl) #no. of players
    #initialize the environment variable
    env = Environment(NumPl, N)
    #now, initialize the players in a loop
    players = [] #the list of players
    for i in range(NumPl): #for each player
        players.append(Player(N, env)) #each player has been initialized

    nextTime = True #this will keep track of the number of time steps in which to keep playing the game
    currentTime = 1
    while (nextTime is True): #basically at each time step each player executes a new thread of execution for picking a strategy
        #and then the process of generating rewards takes place within a lock so that only one player at any one point
        #in time is executing the environment variable for generating rewards
        for j in range(NumPl): #for each of the players, threads will be generated individually per time step
            t = threading.Thread(target=play, args=(players, j, currentTime))
            t.start()
        #now join all the threads before moving on to the next time step
        logging.debug("Waiting for all threads.")
        main_thread = threading.currentThread()
        for t in threading.enumerate():
            if t is not main_thread:
                t.join()

        currentTime = currentTime + 1 #increment the time step by 1
        logging.debug("Moving on to time step %d" % currentTime)
        answer = raw_input("Do you want to play more? (y/n) ")
        if answer == "y":
            nextTime = True
        else:
            nextTime = False
        print("nextTime = %s" % nextTime)

    print("Game over...")





