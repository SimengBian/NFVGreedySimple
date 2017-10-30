import numpy as np
import matplotlib.pyplot as plt

systemInformation = np.load("config/System Information.npz")
Vs = systemInformation['Vs']
lenOfVs = len(Vs)

avgQueueBacklogs = np.load("results/avgQueueBacklogs.npz")['avgQueueBacklogs']
avgEnergyCosts = np.load("results/avgEnergyCosts.npz")['avgEnergyCosts']

x = Vs
y = []
for i in range(lenOfVs):
    y.append(sum(avgQueueBacklogs[i])/500.0)
    # y.append(sum(avgEnergyCosts[i]) / 500.0)

plt.xlabel("V")
plt.ylabel("Average Queue Backlogs")
# plt.ylabel("Average Energy Costs")
plt.plot(x, y, 'b-')
plt.show()

print(x)
print(y)

print("test")