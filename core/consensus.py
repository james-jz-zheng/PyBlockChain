import random as rd
import thread, time

NO_OF_NODES = 500
MAX_NO_OF_CHOSEN_PEERS = 50
MIN_NO_OF_CHOSEN_PEERS = 3

def init_nodes():
    result = []
    for i in range(NO_OF_NODES):
        result.append(rd.randint(0,2))
    return result

def evolve(arr):
    chosen_node = rd.randint(0, NO_OF_NODES-1)
    while arr[chosen_node] == 2:
        chosen_node = rd.randint(0, NO_OF_NODES-1)

    NO_OF_CHOSEN_PEERS = rd.randint(MIN_NO_OF_CHOSEN_PEERS, MAX_NO_OF_CHOSEN_PEERS)
    chosen_peers = [rd.randint(0, NO_OF_NODES-1) for x in range(NO_OF_CHOSEN_PEERS)]
    if chosen_node in chosen_peers: chosen_peers.remove(chosen_node)

    count = 1
    sum = arr[chosen_node]
    for p in chosen_peers:
        vp = arr[p]
        if vp != 2:
            count += 1
            sum += vp


    arr[chosen_node] = 1 if sum > count/2.0 else arr[chosen_node]
    return arr


data_for_plot = []
a = init_nodes()
for i in range(500):
    a = evolve(a)
    # print(''.join([str(y) if y !=2 else ' ' for y in a]))
    count_0 = len([x for x in a if x == 0])
    count_1 = len([x for x in a if x == 1])
    # print (i, count_0, count_1)
    data_for_plot.append((i, count_0, count_1))

data_for_plot_x, data_for_plot_y, data_for_plot_z = zip(*data_for_plot)

import numpy as np
import matplotlib.pyplot as plt

# red dashes, blue squares and green triangles
plt.plot(data_for_plot_x, data_for_plot_y, 'rs', data_for_plot_x, data_for_plot_z, 'b^')
plt.show()
