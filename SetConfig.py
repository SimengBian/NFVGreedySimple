import random
import numpy as np

'''
Network Function (NF)
'''
numOfNF = 4  # number of NF types

# processingCost = [0 for f in range(numOfNF)]
processingCost = np.zeros(numOfNF)
for f in range(numOfNF):
    processingCost[f] = 1

'''
Service Chain (SC)
'''
numOfSC = 3  # number of Service Chain types
lengthOfSC = 3

#  Here the service chains are generated randomly
serviceChains = {c: [] for c in range(numOfSC)}
c = 0
while True:
    if c >= numOfSC:
        break

    NFs = list(range(numOfNF))  # the networks function {0,1,2,...,F-1}
    random.shuffle(NFs)
    chain = NFs[0:lengthOfSC]  # the chosen service chain
    if chain not in serviceChains.values():  # if it is new
        serviceChains[c] = chain  # added it to the dictionary
        c += 1

#  serviceChainsNew[c][i] is the i-th NF of SC type c
serviceChainsNew = (-1) * np.ones((numOfSC, lengthOfSC), dtype=int)
for c in range(numOfSC):
    for i in range(lengthOfSC):
        serviceChainsNew[c][i] = serviceChains[c][i]

#  Here each service chain may have different arrival rates
# arrivalRates = [0 for c in range(numOfSC)]
arrivalRates = np.zeros(numOfSC)
for c in range(numOfSC):
    arrivalRates[c] = 2


'''
Substrate Network (SN)
'''
numOfServer = 5  # number of servers

serverCapacities = np.zeros(numOfServer)
for c in range(numOfServer):
    serverCapacities[c] = 2

idleEnergies = np.zeros(numOfServer)
for c in range(numOfServer):
    idleEnergies[c] = 0

maxEnergies = np.zeros(numOfServer)
for c in range(numOfServer):
    maxEnergies[c] = 10

'''
System Information
'''
maxTime = 5
Vs = [1, 2]

#  arrivals[c, t] is the number of arrival requests of SC type c at time-slot t
arrivals = np.zeros((numOfSC, maxTime))
procs = {
    'exp': (lambda lam: random.expovariate(lam)),
    'pareto': (lambda alpha: random.paretovariate(0.999*alpha+1)-1),
    'uni': (lambda r: random.uniform(0, 2.0/r)),
    'normal': (lambda r: max(0, random.normalvariate(1.0/r, 0.005))),
    'constant': (lambda r: 1.0/r),
    # 'trace': interval_generator
}


def generate(maxTime, arrRate, arrProc):
    totalArrivals = np.zeros(maxTime)
    currentTime = 0
    arrivalTimePoints = []
    while currentTime < maxTime:
        interval = arrProc(arrRate)
        currentTime += interval
        arrivalTimePoints.append(currentTime)

    t = 1
    for p in arrivalTimePoints:
        if p <= t:
            totalArrivals[t-1] += 1
        else:
            t += 1
            if t > maxTime:
                break
            totalArrivals[t-1] += 1

    return totalArrivals


for c in range(numOfSC):
        arrivals[c, :] = generate(maxTime, arrivalRates[c], procs['exp'])

# print(np.sum(arrivals))
np.savez("config/NF Information.npz", numOfNF=numOfNF, processingCost=processingCost)
np.savez("config/SC Information.npz", numOfSC=numOfSC, lengthOfSC=lengthOfSC, serviceChains=serviceChainsNew, arrivalRates=arrivalRates)
np.savez("config/SN Information.npz", numOfServer=numOfServer, serverCapacities=serverCapacities, idleEnergies=idleEnergies, maxEnergies=maxEnergies)
np.savez("config/System Information", maxTime=maxTime, arrivals=arrivals, Vs=Vs)