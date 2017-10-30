import numpy as np

# Load configurations
scInformation = np.load("config/SC Information.npz")
nfInformation = np.load("config/NF Information.npz")
snInformation = np.load("config/SN Information.npz")
systemInformation = np.load("config/System Information.npz")

# System Information
maxTime = systemInformation['maxTime']
Vs = systemInformation['Vs']
lenOfVs = len(Vs)
arrivals = systemInformation['arrivals']  # arrivals[c, t]

# Network Information
numOfNF = nfInformation['numOfNF']
processingCost = nfInformation['processingCost']  # processingCost[f]

# Service Chain Information
numOfSC = scInformation['numOfSC']
lengthOfSC = scInformation['lengthOfSC']
serviceChains = scInformation['serviceChains']  # serviceChains[c, i]

# Substrate Network Information (mainly about the servers)
numOfServer = snInformation['numOfServer']
serverCapacities = snInformation['serverCapacities']  # serverCapacities[s]
idleEnergies = snInformation['idleEnergies']  # idleEnergies[s]
maxEnergies = snInformation['maxEnergies']  # maxEnergies[s]

# the observed states of **previous** time-slot, we maintain states for each parameter V

# queueBacklogs[V][s, f, c] saves the queue backlogs of server s, VM f, type c.
# (Notice that f here means both Network Functions and VMs on the server)
queueBacklogs = {V: np.zeros((numOfServer, numOfNF, numOfSC), dtype=int) for V in Vs}

# VMStates[V][s, f] maintains the on-off states of the VM f on server s. "True" means "on" and "False" means "off".
# VMStates = {V: np.zeros((numOfServer, numOfNF), dtype=bool) for V in Vs}

# resourceAllocations[V][s, f, c] denotes how many resources is allocated to type c on VM f, on server s.
resourceAllocations = {V: np.zeros((numOfServer, numOfNF, numOfSC), dtype=int) for V in Vs}
actualServices = {V: np.zeros((numOfServer, numOfNF, numOfSC), dtype=int) for V in Vs}

# placements[V][(c, f)] = s means the NF f of service chain c is placed on server s
placements = {V: {} for V in Vs}

avgQueueBacklogs = {V: np.zeros(maxTime) for V in Vs}
avgEnergyCosts = {V: np.zeros(maxTime) for V in Vs}


def VNFPlacement(V, queues):
    # print("VNFPlacement")
    placement = {}
    #  For each service chain type c, and one of its function f, we need to decide on which server to place it
    for c in range(numOfSC):
        for i in range(lengthOfSC):
            f = serviceChains[c][i]
            pair = tuple([c, f])
            queue = queues[:, f, c]
            chosenServer = np.argmin(queue)
            placement[pair] = chosenServer

    return placement


def ResourceAllocation(V, queues):
    # print("ResourceAllocation")
    allocation = np.zeros((numOfServer, numOfNF, numOfSC))
    for s in range(numOfServer):
        term1 = V * (maxEnergies[s] - idleEnergies[s]) / float(serverCapacities[s])
        weights = term1 * np.ones((numOfNF, numOfSC))
        for f in range(numOfNF):
            for c in range(numOfSC):
                weights[f, c] -= queues[s, f, c] / float(processingCost[f])
        (chosenVM, chosenType) = np.unravel_index(weights.argmin(), weights.shape)
        if weights[chosenVM, chosenType] < 0:
            allocation[s, chosenVM, chosenType] = serverCapacities[s]

    return allocation


def QueueUpdate(V, queues, services, placement):
    # print("QueueUpdate")
    for s in range(numOfServer):
        for f in range(numOfNF):
            for c in range(numOfSC):
                queues[s, f, c] -= services[s, f, c]
                if tuple([c, f]) in placement.keys() and placement[tuple([c, f])] == s:
                    if f == serviceChains[c][0]:
                        queues[s, f, c] += arrivals[c][t]
                    else:
                        chain = list(serviceChains[c, :])
                        fPre = serviceChains[c][chain.index(f) - 1]
                        for ss in range(numOfServer):
                            queues[s, f, c] += services[ss, fPre, c]

    return queues


def ServiceUpdate(V, queues, allocation):
    # print("ServiceUpdate")
    services = np.zeros((numOfServer, numOfNF, numOfSC))
    for s in range(numOfServer):
        for f in range(numOfNF):
            for c in range(numOfSC):
                services[s, f, c] = min(allocation[s, f, c] / processingCost[f], queues[s, f, c])

    return services


def VNFGreedy(t, V):
    '''
    :param t: current time-slot.
    :param V: the trade-off parameter of queue backlog and cost
    :return: the total queue backlogs and total energy cost incurred in this time-slot
    '''
    global queueBacklogs, VMStates, resourceAllocations, placements

    # Part 1: calculate placements
    placements[V] = VNFPlacement(V, queueBacklogs[V])

    queueBacklogs[V] = QueueUpdate(V, queueBacklogs[V], actualServices[V], placements[V])

    resourceAllocations[V] = ResourceAllocation(V, queueBacklogs[V])

    actualServices[V] = ServiceUpdate(V, queueBacklogs[V], resourceAllocations[V])


def calculateAvgQueueBacklog(V):
    queues = queueBacklogs[V]
    total = 0
    for s in range(numOfServer):
        for f in range(numOfNF):
            for c in range(numOfSC):
                total += queues[s, f, c]

    # return total/float(numOfServer * numOfNF * numOfSC)
    return total


def calculateAvgEnergyCost(V):
    services = actualServices[V]
    total = 0
    for s in range(numOfServer):
        for f in range(numOfNF):
            for c in range(numOfSC):
                total += services[s, f, c] * processingCost[f]

    # return total/float(numOfServer * numOfNF * numOfSC)
    return total

if __name__ == "__main__":
    for V in Vs:
        for t in range(maxTime):
            print("Now V is", V, " and time slot is", t)
            VNFGreedy(t, V)
            avgQueueBacklogs[V][t] = calculateAvgQueueBacklog(V)
            avgEnergyCosts[V][t] = calculateAvgEnergyCost(V)

    avgQueueBacklogsNew = np.zeros((lenOfVs, maxTime))
    avgEnergyCostsNew = np.zeros((lenOfVs, maxTime))
    for i in range(lenOfVs):
        avgQueueBacklogsNew[i, :] = np.array(avgQueueBacklogs[Vs[i]])
        avgEnergyCostsNew[i, :] = np.array(avgEnergyCosts[Vs[i]])

    np.savez("results/avgQueueBacklogs.npz", avgQueueBacklogs=avgQueueBacklogsNew)
    np.savez("results/avgEnergyCosts.npz", avgEnergyCosts=avgEnergyCostsNew)
    print("main")