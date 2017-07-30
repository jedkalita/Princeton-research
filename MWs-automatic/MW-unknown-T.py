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
        self.costs = costs #get the cost ector per player per strategy executed for all their scenarios and store it

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
            #print("Total Scenarios = %d" %totalScenarios)
            '''print("Printing cost vector inside environment......")
            print(self.costs)
            print(self.costs[1][1][1])'''
            expectedCost = 0
            if totalScenarios == 0:
                expectedCost = self.costs[playerID][pickedStrategy][0]
            else:
                #print(self.costs[playerID][pickedStrategy])
                for i in range(0, totalScenarios): #each scenario encoding a particular representation of opponents' strategies
                    '''print("Before cost")
                    print("Player id = %d" %playerID)
                    print("Picked strategy = %d" % pickedStrategy)
                    print("i = %d" %i)
                    print(self.costs[playerID][pickedStrategy][i])
                    print(self.costs[playerID][pickedStrategy][i][i])'''
                    #print(self.costs[playerID][pickedStrategy][0][i])
                    cost = self.costs[playerID][pickedStrategy][0][i] #cost aganist a config
                    #print("After cost = %f" %cost)
                    expectedCost = expectedCost + cost #keep the sum count
                expectedCost = (expectedCost * 1.0) / (totalScenarios * 1.0) #to get the expectation
        finally:
            logging.debug("Released a lock for for player = %d" % playerID)
            self.lock.release()
            print("Expected Cost = %f" %expectedCost)
            return expectedCost #this is the cost needed by player who picked the strategy

class Player:
    def __init__(self, N, env):
        self.N = N #the number of actions/strategies that the player has
        self.weight = np.ones((self.N), dtype=float) #each player will have their cost vector indexed acc to the time instance
        #this has been initialized to 1.0 for all, but we really only care about for t=1 for all actions acc to the
        #algorithm
        #self.cost = np.zeros(self.N, self.T) #the cost vector for each individual player that will be getting filled
        #for the time t after they have chosen their action, being updated upon by the environment/adversary
        #self.epsilon = math.sqrt(math.log(self.N) / self.T) #the value of learning parameter for the no regret case
        # under known T
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
        '''try:
            t = self.env.generateRewards(playerID, pickedStrategy)
            print("after calling generate rewards.....")
            print("PlayerId = %d, picked stretegy = %d" %playerID %pickedStrategy)
            print("The expected cost returned is : %d" % t)
        except TypeError as te:
            print("Picked up a TypeError.!")'''
        self.weight[pickedStrategy] = self.weight[pickedStrategy] * math.pow((1 - epsilon),
                                                                             self.env.generateRewards(playerID,
                                                                                                      pickedStrategy))
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
    NumPl = int(fh.readline()) # no. of players
    N = int(fh.readline())  # total no. of actions
    #print("Time horizon entered : ", T, ". No. of actions: ", N, ". No. of players: ", NumPl)

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
            # print("curr = %d" %curr)
            # print("player costs[i][j] : %s" % playerCosts[i][j])
            curr = 0 #to iterate over how many scenarios are there to index in properly
            tmp = playerCosts[i][j].split(" ")
            for k in range(scenarios):
                # print(tmp)
                # print(tmp[curr])
                # print("Str format %s" % tmp[curr])
                costs[i][j][curr] = float(tmp[curr])
                #print(costs[i][j][curr])
                curr = curr + 1
    '''print("Printing the costs vector.....")
    print(costs)
    print(costs[1][1][1])'''
    #initialize the environment variable
    env = Environment(NumPl, N, costs)
    #now, initialize the players in a loop
    players = [] #the list of players
    for i in range(NumPl): #for each player
        players.append(Player(NumPl, env)) #each player has been initialized

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
