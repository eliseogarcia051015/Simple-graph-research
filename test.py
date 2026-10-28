import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import numpy as np
import networkx as nx


# --------------------------------------------------
# Graphs: all have 7 vertices
# --------------------------------------------------

T1 = {
    1: [2],
    2: [1, 3],
    3: [2, 4, 6],
    4: [3, 5],
    5: [4],
    6: [3, 7],
    7: [6]
}

T2 = {
    1: [2],
    2: [1, 3],
    3: [2, 4],
    4: [3, 5, 6],
    5: [4],
    6: [4, 7],
    7: [6]
}

P = {
    1: [2],
    2: [1, 3],
    3: [2, 4],
    4: [3, 5],
    5: [4, 6],
    6: [5, 7],
    7: [6]
}

C = {
    1: [7, 2],
    2: [1, 3],
    3: [2, 4],
    4: [3, 5],
    5: [4, 6],
    6: [5, 7],
    7: [6, 1]
}

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
# Simulation helpers
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


def simulate(graph, start_a, start_b):
    position_a = start_a
    position_b = start_b

    path_a = [position_a]
    path_b = [position_b]
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
            position_a = random.choice(graph[old_a])
            position_b = random.choice(graph[old_b])

        T += 1
        path_a.append(position_a)
        path_b.append(position_b)

        # Stop at the first time both walkers occupy the same vertex.
        if position_a == position_b:
            T1 = T
            break

    # Keep the same counting rule as the original program:
    # count distinct vertices visited at times 1 through T1 - 1.
    counted_a = set(path_a[1:-1])
    counted_b = set(path_b[1:-1])

    number_a = len(counted_a)
    number_b = len(counted_b)
    total_vertices = len(graph)

    percent_a = 100 * number_a / total_vertices
    percent_b = 100 * number_b / total_vertices

    return T1, number_a, number_b, percent_a, percent_b, path_a, path_b


# --------------------------------------------------
# One-window dashboard
# --------------------------------------------------

class GraphDashboard:
    def __init__(self, graph_data, number_of_runs):
        self.graph_data = graph_data
        self.graph_names = list(graph_data.keys())
        self.graph_index = 0
        self.run_index = 0
        self.view = "traversal"
        self.anim = None
        self.animation_frame = 0

        # Run every simulation once and keep the results in memory.
        # Navigation and view switching do not rerun the simulations.
        for name, graph in self.graph_data.items():
            (start_a, start_b), distance = find_farthest_vertices(graph)

            results = []
            paths = []

            for _ in range(number_of_runs):
                T1, number_a, number_b, percent_a, percent_b, path_a, path_b = (
                    simulate(graph, start_a, start_b)
                )
                results.append(
                    (T1, number_a, number_b, percent_a, percent_b)
                )
                paths.append((path_a, path_b, T1))

            self.graph_data[name] = {
                "graph": graph,
                "start_a": start_a,
                "start_b": start_b,
                "distance": distance,
                "results": results,
                "paths": paths
            }

        self.fig = plt.figure(figsize=(13, 8))
        self.fig.canvas.manager.set_window_title("Random Walk Graph Dashboard")

        # The graph and histogram views share the same window.
        self.ax_graph = self.fig.add_axes([0.05, 0.19, 0.90, 0.72])
        self.hist_axes = [
            self.fig.add_axes([0.07, 0.56, 0.25, 0.25]),
            self.fig.add_axes([0.38, 0.56, 0.25, 0.25]),
            self.fig.add_axes([0.69, 0.56, 0.25, 0.25]),
            self.fig.add_axes([0.22, 0.20, 0.25, 0.25]),
            self.fig.add_axes([0.53, 0.20, 0.25, 0.25])
        ]

        # Navigation and view buttons.
        self.buttons = []
        self._add_button([0.04, 0.08, 0.12, 0.055], "Previous Graph", self.previous_graph)
        self._add_button([0.17, 0.08, 0.12, 0.055], "Next Graph", self.next_graph)
        self._add_button([0.31, 0.08, 0.17, 0.055], "Graph Traversal View", self.show_traversal)
        self._add_button([0.50, 0.08, 0.15, 0.055], "Data / Histogram", self.show_histograms)
        self._add_button([0.68, 0.08, 0.10, 0.055], "Previous Walk", self.previous_walk)
        self._add_button([0.79, 0.08, 0.09, 0.055], "Next Walk", self.next_walk)
        self._add_button([0.89, 0.08, 0.08, 0.055], "Random Walk", self.random_walk)

        self._add_button([0.43, 0.015, 0.14, 0.05], "Replay Walk", self.replay_walk)

        self._set_view_visibility()
        self.draw_current_view()
        plt.show()

    def _add_button(self, rect, label, callback):
        ax = self.fig.add_axes(rect)
        button = Button(ax, label)
        button.on_clicked(callback)
        self.buttons.append(button)

    def current_name(self):
        return self.graph_names[self.graph_index]

    def current_data(self):
        return self.graph_data[self.current_name()]

    def _stop_animation(self):
        if self.anim is not None and self.anim.event_source is not None:
            self.anim.event_source.stop()
        self.anim = None

    def _set_view_visibility(self):
        traversal_visible = self.view == "traversal"
        self.ax_graph.set_visible(traversal_visible)

        for ax in self.hist_axes:
            ax.set_visible(not traversal_visible)

    def draw_current_view(self):
        self._stop_animation()
        self._set_view_visibility()

        if self.view == "traversal":
            self.draw_traversal()
        else:
            self.draw_histograms()

        self.fig.canvas.draw_idle()

    def previous_graph(self, event):
        self.graph_index = (self.graph_index - 1) % len(self.graph_names)
        self.run_index = 0
        self.animation_frame = 0
        self.draw_current_view()

    def next_graph(self, event):
        self.graph_index = (self.graph_index + 1) % len(self.graph_names)
        self.run_index = 0
        self.animation_frame = 0
        self.draw_current_view()

    def show_traversal(self, event):
        self.view = "traversal"
        self.draw_current_view()

    def show_histograms(self, event):
        self.view = "histograms"
        self.draw_current_view()

    def previous_walk(self, event):
        self.run_index = (self.run_index - 1) % len(self.current_data()["paths"])
        self.animation_frame = 0
        if self.view == "traversal":
            self.draw_current_view()

    def next_walk(self, event):
        self.run_index = (self.run_index + 1) % len(self.current_data()["paths"])
        self.animation_frame = 0
        if self.view == "traversal":
            self.draw_current_view()

    def random_walk(self, event):
        self.run_index = random.randrange(len(self.current_data()["paths"]))
        self.animation_frame = 0
        if self.view == "traversal":
            self.draw_current_view()

    def replay_walk(self, event):
        self.animation_frame = 0
        if self.view == "traversal":
            self.draw_current_view()

    def draw_traversal(self):
        data = self.current_data()
        graph = data["graph"]
        path_a, path_b, T1 = data["paths"][self.run_index]

        G = nx.Graph()
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                G.add_edge(node, neighbor)

        name = self.current_name()

        if name == "Straight line":
            pos = {node: (node - 1, 0) for node in graph}
        elif name == "Cycle":
            pos = {
                1: (0, 1.5), 2: (1.2, 1), 3: (1.5, -0.2),
                4: (0.7, -1.2), 5: (-0.7, -1.2),
                6: (-1.5, -0.2), 7: (-1.2, 1)
            }
        elif name == "Tree T3":
            pos = {
                1: (0, 2), 2: (1, 2), 3: (0.8, 1.0),
                4: (2, 2), 5: (3, 2), 6: (3.8, 1),
                7: (3.8, 3)
            }
        elif name == "Spider tree 1":
            pos = {
                1: (0, 1), 2: (1, 1), 3: (2, 1), 4: (3, 1),
                5: (4, 1), 6: (2, 0), 7: (2, -1)
            }
        else:
            pos = {
                1: (0, 1), 2: (1, 1), 3: (2, 1), 4: (3, 1),
                5: (4, 1), 6: (3, 0), 7: (3, -1)
            }

        self.ax_graph.clear()
        self.ax_graph.set_axis_off()

        def update(frame):
            self.animation_frame = frame
            self.ax_graph.clear()
            self.ax_graph.set_axis_off()

            current_a = path_a[frame]
            current_b = path_b[frame]

            nx.draw_networkx_edges(G, pos, width=2, edge_color="gray", ax=self.ax_graph)
            nx.draw_networkx_nodes(
                G, pos, node_size=700, node_color="lightgray", ax=self.ax_graph
            )
            nx.draw_networkx_labels(
                G, pos, font_size=12, font_weight="bold", ax=self.ax_graph
            )

            if current_a == current_b and frame == T1:
                nx.draw_networkx_nodes(
                    G, pos, nodelist=[current_a], node_size=950,
                    node_color="red", ax=self.ax_graph
                )
                title = (
                    f"{name} | Run {self.run_index + 1}/{len(data['paths'])}\n"
                    f"COLLISION at t = {T1}, node {current_a}"
                )
                self.ax_graph.set_title(title, color="red", fontsize=14, fontweight="bold")
            else:
                colors = []
                sizes = []
                for node in G.nodes():
                    if node == current_a and node == current_b:
                        colors.append("purple")
                        sizes.append(900)
                    elif node == current_a:
                        colors.append("skyblue")
                        sizes.append(800)
                    elif node == current_b:
                        colors.append("orange")
                        sizes.append(800)
                    else:
                        colors.append("lightgray")
                        sizes.append(700)

                nx.draw_networkx_nodes(
                    G, pos, nodelist=list(G.nodes()),
                    node_size=sizes, node_color=colors, ax=self.ax_graph
                )
                self.ax_graph.set_title(
                    f"{name} | Run {self.run_index + 1}/{len(data['paths'])}\n"
                    f"t = {frame}/{T1}   A: node {current_a}   B: node {current_b}",
                    fontsize=13
                )

        self.anim = animation.FuncAnimation(
            self.fig, update, frames=len(path_a), interval=600, repeat=False
        )
        update(min(self.animation_frame, len(path_a) - 1))

    def draw_histograms(self):
        data = self.current_data()
        results = data["results"]

        T_values = [row[0] for row in results]
        A_values = [row[1] for row in results]
        B_values = [row[2] for row in results]
        A_percentages = [row[3] for row in results]
        B_percentages = [row[4] for row in results]

        data_sets = [
            (T_values, "First collision time ($T_1$)", "Time steps"),
            (A_values, "Distinct vertices visited by A", "Number of vertices"),
            (B_values, "Distinct vertices visited by B", "Number of vertices"),
            (A_percentages, "Percentage visited by A", "Percentage (%)"),
            (B_percentages, "Percentage visited by B", "Percentage (%)")
        ]

        for ax, (values, title, xlabel) in zip(self.hist_axes, data_sets):
            ax.clear()
            if xlabel == "Percentage (%)":
                bins = np.linspace(-100 / 14, 100 + 100 / 14, 16)
            else:
                bins = np.arange(min(values) - 0.5, max(values) + 1.5, 1)

            ax.hist(values, bins=bins, edgecolor="black")
            ax.set_title(title, fontsize=10)
            ax.set_xlabel(xlabel, fontsize=9)
            ax.set_ylabel("Frequency", fontsize=9)
            ax.grid(axis="y", alpha=0.3)

        self.fig.suptitle(
            f"Data / Histogram View — {self.current_name()} "
            f"({len(results)} simulations)",
            fontsize=15
        )

        summary = (
            f"Average T1: {np.mean(T_values):.2f}     "
            f"Average |VA|: {np.mean(A_values):.2f}     "
            f"Average |VB|: {np.mean(B_values):.2f}\n"
            f"Average A visited: {np.mean(A_percentages):.2f}%     "
            f"Average B visited: {np.mean(B_percentages):.2f}%"
        )
        self.fig.text(0.5, 0.145, summary, ha="center", va="center", fontsize=10)

        self.fig.canvas.draw_idle()


# --------------------------------------------------
# Main program
# --------------------------------------------------

def main():
    number_of_runs = 1000

    print("Simulating all graphs...")
    print("Results will be kept in memory while you navigate the dashboard.")

    # Build the dashboard once; no extra windows are opened per graph.
    GraphDashboard(graphs, number_of_runs)


if __name__ == "__main__":
    main()