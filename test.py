#one walker
import random 
import matplotlib.pyplot as plt
import numpy as np #do something with this later

def print_simulate(graph):
    count = 0
    current = 3
    visited = {current}
    walk = []

    while len(visited) < len(graph):
        walk.append(current)
        neighbors = graph[current]

        print("Current:", current)
        print("Neighbors:", neighbors)

        next_vertex = random.choice(neighbors)
        count+=1
        current = next_vertex
        visited.add(current)

        print("Moved to:", current)
        print("Visited:", visited)
        print()
    walk.append(current)
    print(f"Number of moves: {count}")
    print(f"Walk: {walk}")
    print("Finished!")



def simulate(graph):
    count = 0
    current = 3
    visited = {current}

    while len(visited) < len(graph):
        neighbors = graph[current]

        next_vertex = random.choice(neighbors)
        count+=1
        current = next_vertex
        visited.add(current)

    return count

def view_data(data):
    print("min steps up to highest steps, show frequency with histogram")
    bins = np.arange(min(data) - 0.5, max(data) + 1.5, 1)
    print(f"Minimum steps needed: {min(data)}")
    print(f"Max steps needed: {max(data)}")
    
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=bins, edgecolor='black', color='skyblue', alpha=0.8, density=False)

    plt.title('Distribution of Total Steps in a 1-Walker Random Walk Simulation', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Steps to Visit All Vertices', fontsize=12)
    plt.ylabel('Frequency (Simulation Counts)', fontsize=12)
    
    mean_steps = np.mean(data)
    plt.axvline(mean_steps, color='red', linestyle='dashed', linewidth=1.5, label=f'Mean Steps ({mean_steps:.2f})')
    
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    graph = { #straight line/walk
        1: [2],
        2: [1, 3],
        3: [2, 4],
        4: [3, 5],
        5: [4]
    }

    graph2 = {
        1: [2],
        2: [1,3],
        3: [2,4],
        4: [3,5],
        5: [4, 6],
        6: [5, 7],
        7: [6, 8],
        8: [7, 9],
        9: [8, 10],
        10: [9],
    }
    #print(print_simulate(graph))

    number_of_simulations = 100000
    steps_needed = [] #sotres it
    for i in range(number_of_simulations):
        steps = simulate(graph)
        steps_needed.append(steps)
        #print(f"Simulation {i+1} needed {steps} steps")
    ordered = sorted(steps_needed)
    #print(ordered)
    view_data(ordered)

if __name__ == '__main__':
    main()