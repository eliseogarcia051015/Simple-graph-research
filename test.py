import random 

def view_simulate(graph):
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

def main():
    graph = { #straight line/walk
        1: [2],
        2: [1, 3],
        3: [2, 4],
        4: [3, 5],
        5: [4]
    }
    number_of_simulations = 10
    steps_needed = [] #sotres it
    for i in range(number_of_simulations):
        steps = simulate(graph)
        steps_needed.append(steps)
        print(f"Simulation {i+1} needed {steps} steps")


if __name__ == '__main__':
    main()