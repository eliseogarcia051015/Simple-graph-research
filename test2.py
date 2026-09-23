# two walkers
import random

graph1 = {
    1: [2],
    2: [1, 3],
    3: [2, 4],
    4: [3, 5],
    5: [4]
}

graph2 = {
    1: [2],
    2: [1, 3],
    3: [2, 4],
    4: [3, 5],
    5: [4, 6],
    6: [5, 7],
    7: [6, 8],
    8: [7, 9],
    9: [8, 10],
    10: [9]
}

count = 0

curr_A = 1
curr_B = 5

visited_A = {curr_A}
visited_B = {curr_B}

walk_A = [curr_A]
walk_B = [curr_B]


while (len(visited_A) < len(graph1)
       and len(visited_B) < len(graph1)
       and curr_A != curr_B):
    prob = random.random()

    # A moves
    if prob < 1/3:
        neighbors = graph1[curr_A]
        curr_A = random.choice(neighbors)
        visited_A.add(curr_A)
        walk_A.append(curr_A)

    # B moves
    elif prob < 2/3:
        neighbors = graph1[curr_B]
        curr_B = random.choice(neighbors)
        visited_B.add(curr_B)
        walk_B.append(curr_B)

    # Neither moves
    else:
        walk_A.append(curr_A)
        walk_B.append(curr_B)

    count += 1


print("Finished!")
print("Number of moves:", count)
print("A's walk:", walk_A)
print("B's walk:", walk_B)
print("A visited:", visited_A)
print("B visited:", visited_B)

if curr_A == curr_B:
    print("A and B touched each other!")

elif len(visited_A) == len(graph1):
    print("A visited every vertex!")

elif len(visited_B) == len(graph1):
    print("B visited every vertex!")