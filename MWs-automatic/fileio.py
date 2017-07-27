import sys
import numpy as np
nof = raw_input("Enter name of file (rps/ct(.txt)) : ")
f = open(nof, 'r')
#print(f.readline())
numPlayers = int(f.readline())
print("No of players : %d" % numPlayers)
numStrategies = int(f.readline())
print("No of players : %d" % numStrategies)
#print(f.readline())
scenarios = (numPlayers - 1) * numStrategies
playerCosts = []
for i in range(numPlayers):
    strategiesPerPlayer = []
    for j in range(numStrategies):
        strategiesPerPlayer.append(f.readline().replace('\n', ''))
    playerCosts.append(strategiesPerPlayer)
'''a = playerCosts[0].split()
print(a)'''

'''cost = f.readline().replace('\n', '')
print(cost)
scenarios = cost.split(' ')
print(scenarios)'''
print(playerCosts)
costs = np.zeros((numPlayers, numStrategies, scenarios), dtype=float)
for i in range(len(playerCosts)):

    for j in range(len(playerCosts[i])):
        #print("curr = %d" %curr)
        #print("player costs[i][j] : %s" % playerCosts[i][j])
        curr = 0
        tmp = playerCosts[i][j].split(" ")
        for k in range(scenarios):
            #print(tmp)
            #print(tmp[curr])
            #print("Str format %s" % tmp[curr])
            costs[i][j][curr] = float(tmp[curr])
            #print(costs[i][j][curr])
            curr = curr + 1

print(costs)
#with open('rps.txt', 'r') as input:
#   print()
