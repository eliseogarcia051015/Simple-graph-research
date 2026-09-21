import random

graph = { #straight line/walk
    1: [2],
    2: [1, 3],
    3: [2, 4],
    4: [3, 5],
    5: [4]
}

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