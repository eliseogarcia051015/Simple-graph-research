import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import numpy as np
import networkx as nx


# --------------------------------------------------
# Graphs: all have 7 vertices
# --------------------------------------------------
# T1: spider tree
T1 = {
    1: [2],  # Alice
    2: [1, 3],
    3: [2, 4, 6],
    4: [3, 5],
    5: [4],  # Bob
    6: [3, 7],
    7: [6]
}

# T2: spider tree
T2 = {
    1: [2],  # Alice
    2: [1, 3],
    3: [2, 4],
    4: [3, 5, 6],
    5: [4],
    6: [4, 7],
    7: [6]  # Bob
}

# P: straight line (path)
P = {
    1: [2],  # Alice
    2: [1, 3],
    3: [2, 4],
    4: [3, 5],
    5: [4, 6],
    6: [5, 7],
    7: [6]  # Bob
}

# C: cycle
C = {
    1: [7, 2],
    2: [1, 3],  # Alice
    3: [2, 4],
    4: [3, 5],
    5: [4, 6],
    6: [5, 7],  # Bob
    7: [6, 1]
}

# T3: shape
T3 = {
    1: [2],
    2: [1, 3, 4],
    3: [2],
    4: [2, 5],
    5: [4, 6, 7],
    6: [5],
    7: [5]
}


graphs = {
    "Spider tree 1": T1,
    "Spider tree 2": T2,
    "Straight line": P,
    "Cycle": C,
    "Tree T3": T3
}


# --------------------------------------------------
# Find shortest distances between vertices
# --------------------------------------------------
def shortest_distances(graph, start):
    distances = {start: 0}
    queue = [start]

    while queue:
        current = queue.pop(0)

        for neighbor in graph[current]:
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    return distances


# --------------------------------------------------
# Find the two farthest-apart vertices
# --------------------------------------------------
def find_farthest_vertices(graph):
    vertices = list(graph.keys())

    farthest_pair = (vertices[0], vertices[1])
    max_distance = -1

    for start in vertices:
        distances = shortest_distances(graph, start)

        for end in vertices:
            if distances[end] > max_distance:
                max_distance = distances[end]
                farthest_pair = (start, end)

    return farthest_pair, max_distance


# --------------------------------------------------
# Simulate two random walkers
# --------------------------------------------------
def simulate(graph, start_a, start_b):

    position_a = start_a
    position_b = start_b

    path_a = [position_a]
    path_b = [position_b]

    visited_a = {position_a}
    visited_b = {position_b}

    T = 0

    while True:

        event = random.choice(["A", "B", "both"])
        old_a = position_a
        old_b = position_b

        if event == "A":
            position_a = random.choice(graph[old_a])
        elif event == "B":
            position_b = random.choice(graph[old_b])
        else:
            next_a = random.choice(graph[old_a])
            next_b = random.choice(graph[old_b])
            position_a = next_a
            position_b = next_b

        T += 1
        path_a.append(position_a)
        path_b.append(position_b)

        if position_a == position_b:
            T1 = T
            break

        visited_a.add(position_a)
        visited_b.add(position_b)

    counted_a = set(path_a[1:-1])
    counted_b = set(path_b[1:-1])

    number_a = len(counted_a)
    number_b = len(counted_b)

    total_vertices = len(graph)

    percent_a = 100 * number_a / total_vertices
    percent_b = 100 * number_b / total_vertices

    return T1, number_a, number_b, percent_a, percent_b, path_a, path_b


# --------------------------------------------------
# Interactive Traversal Viewer with Buttons & Clean Layouts
# --------------------------------------------------
class InteractiveWalkViewer:
    def __init__(self, name, graph_dict, paths_list):
        self.name = name
        self.graph_dict = graph_dict
        self.paths_list = paths_list
        self.current_run_idx = 0

        self.G = nx.Graph()
        for node, neighbors in graph_dict.items():
            for n in neighbors:
                self.G.add_edge(node, n)

        # Fixed layout positions for clear visualizations
        if "Straight line" in name:
            self.pos = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (3, 0), 5: (4, 0), 6: (5, 0), 7: (6, 0)}
        elif "Cycle" in name:
            self.pos = {
                1: (0, 1.5), 2: (1.2, 1), 3: (1.5, -0.2), 4: (0.7, -1.2),
                5: (-0.7, -1.2), 6: (-1.5, -0.2), 7: (-1.2, 1)
            }
        elif "Tree T3" in name:
            self.pos = {
                1: (0, 2), 2: (1, 2), 3: (0.8, 1.8), 4: (2, 2),
                5: (3, 2), 6: (3.2, 1.8), 7: (4, 2)
            }
        elif "Spider tree 1" in name:
            self.pos = {
                1: (0, 1), 2: (1, 1), 3: (2, 1), 4: (3, 1), 5: (4, 1),
                6: (2, 0), 7: (2, -1)
            }
        elif "Spider tree 2" in name:
            self.pos = {
                1: (0, 1), 2: (1, 1), 3: (2, 1), 4: (3, 1), 5: (4, 1),
                6: (3, 0), 7: (3, -1)
            }
        else:
            self.pos = nx.spring_layout(self.G, seed=42)

        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        plt.subplots_adjust(bottom=0.2)  # Make room at bottom for interactive buttons

        # Define Interactive Buttons ([left, bottom, width, height])
        ax_replay = plt.axes([0.12, 0.05, 0.2, 0.075])
        ax_random = plt.axes([0.35, 0.05, 0.28, 0.075])
        ax_next = plt.axes([0.66, 0.05, 0.22, 0.075])

        self.btn_replay = Button(ax_replay, 'Replay Walk')
        self.btn_replay.on_clicked(self.replay_walk)

        self.btn_random = Button(ax_random, 'Random Walk')
        self.btn_random.on_clicked(self.random_walk)

        self.btn_next = Button(ax_next, 'Next Walk ->')
        self.btn_next.on_clicked(self.next_walk)

        self.anim = None
        self.start_animation()

    def start_animation(self):
        if self.anim and hasattr(self.anim, 'event_source') and self.anim.event_source:
            self.anim.event_source.stop()

        self.path_a, self.path_b, self.T1 = self.paths_list[self.current_run_idx]

        def update(frame):
            self.ax.clear()
            nx.draw_networkx_nodes(self.G, self.pos, node_size=700, node_color='lightgray', ax=self.ax)
            nx.draw_networkx_edges(self.G, self.pos, width=2, edge_color='gray', ax=self.ax)
            nx.draw_networkx_labels(self.G, self.pos, font_size=12, font_weight='bold', ax=self.ax)

            current_a = self.path_a[frame]
            current_b = self.path_b[frame]

            if frame == self.T1 and current_a == current_b:
                nx.draw_networkx_nodes(self.G, self.pos, nodelist=[current_a], node_size=900, node_color='red', ax=self.ax)
                self.ax.set_title(
                    f"Graph: {self.name} (Simulation Run {self.current_run_idx + 1})\n💥 COLLISION! T1 = {self.T1} on Node {current_a}",
                    fontsize=14, fontweight='bold', color='red', pad=15
                )
            else:
                node_colors = []
                node_sizes = []
                for node in self.G.nodes():
                    if node == current_a and node == current_b:
                        node_colors.append('purple')
                        node_sizes.append(900)
                    elif node == current_a:
                        node_colors.append('skyblue')
                        node_sizes.append(800)
                    elif node == current_b:
                        node_colors.append('orange')
                        node_sizes.append(800)
                    else:
                        node_colors.append('lightgray')
                        node_sizes.append(700)
                
                nx.draw_networkx_nodes(self.G, self.pos, nodelist=list(self.G.nodes()), node_size=node_sizes, node_color=node_colors, ax=self.ax)
                self.ax.set_title(
                    f"Graph: {self.name} | Run {self.current_run_idx + 1} of {len(self.paths_list)}\nTimestep: t = {frame} (A on node {current_a}, B on node {current_b})",
                    fontsize=12, pad=15
                )

            self.ax.axis('off')

        self.anim = animation.FuncAnimation(self.fig, update, frames=self.T1 + 1, interval=600, repeat=False)
        self.fig.canvas.draw_idle()

    def replay_walk(self, event):
        self.start_animation()

    def random_walk(self, event):
        self.current_run_idx = random.randint(0, len(self.paths_list) - 1)
        self.start_animation()

    def next_walk(self, event):
        self.current_run_idx = (self.current_run_idx + 1) % len(self.paths_list)
        self.start_animation()


def animate_sample_traversal(name, graph_dict, paths_list):
    viewer = InteractiveWalkViewer(name, graph_dict, paths_list)
    plt.show()


# --------------------------------------------------
# Plot histograms for one graph
# --------------------------------------------------
def plot_histograms(name, results):

    T_values = [row[0] for row in results]
    A_values = [row[1] for row in results]
    B_values = [row[2] for row in results]
    A_percentages = [row[3] for row in results]
    B_percentages = [row[4] for row in results]

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()

    data_sets = [
        (T_values, "First collision time ($T_1$)", "Time steps"),
        (A_values, "Distinct vertices visited by A ($|V_A|$)", "Number of vertices"),
        (B_values, "Distinct vertices visited by B ($|V_B|$)", "Number of vertices"),
        (A_percentages, "Percentage visited by A", "Percentage (%)"),
        (B_percentages, "Percentage visited by B", "Percentage (%)")
    ]

    for ax, (data, title, xlabel) in zip(axes, data_sets):
        if xlabel == "Percentage (%)":
            bins = np.linspace(-100 / 14, 100 + 100 / 14, 16)
        else:
            bins = np.arange(min(data) - 0.5, max(data) + 1.5, 1)

        ax.hist(data, bins=bins, edgecolor="black")
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Frequency")
        ax.grid(axis="y", alpha=0.3)

    axes[5].set_visible(False)
    fig.suptitle(name)
    plt.tight_layout()
    plt.show()


# --------------------------------------------------
# Main program
# --------------------------------------------------
def main():

    number_of_runs = 1000

    for name, graph in graphs.items():

        (start_a, start_b), distance = find_farthest_vertices(graph)

        print("\n" + "=" * 65)
        print(name)
        print("=" * 65)

        print(f"Walker A starts at: {start_a}")
        print(f"Walker B starts at: {start_b}")
        print(f"Farthest distance: {distance}")

        print()
        print(
            f"{'Run':>3} | {'T1':>4} | {'|VA|':>4} | "
            f"{'|VB|':>4} | {'A (%)':>7} | {'B (%)':>7}"
        )

        results = []
        all_paths = []

        for run in range(1, number_of_runs + 1):

            T1, number_a, number_b, percent_a, percent_b, path_a, path_b = simulate(graph, start_a, start_b)
            
            results.append((T1, number_a, number_b, percent_a, percent_b))
            all_paths.append((path_a, path_b, T1))

            print(
                f"{run:3d} | {T1:4d} | {number_a:4d} | "
                f"{number_b:4d} | {percent_a:6.1f}% | "
                f"{percent_b:6.1f}%"
            )

        T_values = [row[0] for row in results]
        A_values = [row[1] for row in results]
        B_values = [row[2] for row in results]
        A_percentages = [row[3] for row in results]
        B_percentages = [row[4] for row in results]

        print("\nSummary:")
        print(f"Average T1: {np.mean(T_values):.2f}")
        print(f"Average |VA|: {np.mean(A_values):.2f}")
        print(f"Average |VB|: {np.mean(B_values):.2f}")
        print(f"Average A visited: {np.mean(A_percentages):.2f}%")
        print(f"Average B visited: {np.mean(B_percentages):.2f}%")

        all_vertices = len(graph)
        count_a_all = sum(value == all_vertices for value in A_values)
        count_b_all = sum(value == all_vertices for value in B_values)

        print(f"A visited all {all_vertices} vertices: {count_a_all}/{number_of_runs} runs")
        print(f"B visited all {all_vertices} vertices: {count_b_all}/{number_of_runs} runs")
        animate_sample_traversal(name, graph, all_paths)

        # Show the histograms
        plot_histograms(name, results)


if __name__ == "__main__":
    main()