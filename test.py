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

print("Hello world!")