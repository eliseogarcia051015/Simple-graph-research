import random
import json
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import numpy as np
import networkx as nx


# --------------------------------------------------
# Configuration Constants (Easily Configurable)
# --------------------------------------------------
NUMBER_OF_RUNS = 10000
VERTEX_COUNTS = [7, 8, 9, 10]
# --------------------------------------------------
# Graph Generators for N = 7, 8, 9, 10
# --------------------------------------------------

def generate_graphs(n):
    """Generates the 5 graph topologies scaled for n vertices."""
    
    # 1. Straight line (Path graph P_n)
    line = {}
    for i in range(1, n + 1):
        neighbors = []
        if i > 1:
            neighbors.append(i - 1)
        if i < n:
            neighbors.append(i + 1)
        line[i] = neighbors

    # 2. Cycle graph C_n
    cycle = {}
    for i in range(1, n + 1):
        prev_node = n if i == 1 else i - 1
        next_node = 1 if i == n else i + 1
        cycle[i] = [prev_node, next_node]

    # 3. Tree T3 (Spine with branched central node and trailing branch)
    t3 = {}
    for i in range(1, n + 1):
        t3[i] = []
    
    # Build a stable tree topology across vertex counts
    # Root/spine structure
    mid = n // 2
    for i in range(1, n):
        t3[i].append(i + 1)
        t3[i + 1].append(i)
    
    # Add extra structural branches based on n to match T3 shape semantics
    if n >= 3:
        # Add a branch off node 2
        if 3 in t3[2]: t3[2].remove(3)
        t3[2].extend([3, 4] if 4 <= n else [3])
        if 2 not in t3[3]: t3[3].append(2)
    
    # Clean up symmetric adjacency and remove duplicate entries
    for node in t3:
        t3[node] = sorted(list(set(t3[node])))

    # 4. Spider Tree 1 (Long spine with legs attached to a central hub)
    spider1 = {}
    for i in range(1, n + 1):
        spider1[i] = []
    
    hub = n // 2
    for i in range(1, n):
        spider1[i].append(i + 1)
        spider1[i + 1].append(i)
    
    # Add legs at the hub
    if hub > 1 and hub < n:
        leg1 = hub - 1
        leg2 = hub + 1
        # Add extra hanging nodes if n >= 8
        if n >= 8:
            extra_node = n
            spider1[hub].append(extra_node)
            spider1[extra_node] = [hub]

    for node in spider1:
        spider1[node] = sorted(list(set(spider1[node])))

    # 5. Spider Tree 2 (Asymmetric spider tree variant)
    spider2 = {}
    for i in range(1, n + 1):
        spider2[i] = []
    
    for i in range(1, n):
        spider2[i].append(i + 1)
        spider2[i + 1].append(i)
    
    if n >= 7:
        branch_point = n - 2
        leaf = n
        spider2[branch_point].append(leaf)
        spider2[leaf] = [branch_point]

    for node in spider2:
        spider2[node] = sorted(list(set(spider2[node])))

    return {
        "Straight line": line,
        "Cycle": cycle,
        "Tree T3": t3,
        "Spider tree 1": spider1,
        "Spider tree 2": spider2
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

        if position_a == position_b:
            T1 = T
            break

    # Distinct vertices visited at times 1 through T1 - 1
    counted_a = set(path_a[1:-1])
    counted_b = set(path_b[1:-1])

    number_a = len(counted_a)
    number_b = len(counted_b)
    total_vertices = len(graph)

    percent_a = 100 * number_a / total_vertices
    percent_b = 100 * number_b / total_vertices

    return T1, number_a, number_b, percent_a, percent_b, path_a, path_b


# --------------------------------------------------
# Results Exporter (CSV & JSON)
# --------------------------------------------------
def export_results(master_data):
    """Saves all simulation metrics, probability distributions, and coverage stats into JSON and CSV files."""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "simulation_outputs")

    os.makedirs(output_dir, exist_ok=True)
    summary_export = {}

    for (n_verts, name), data in master_data.items():
        results = data["results"]
        total_runs = len(results)
        total_vertices = len(data["graph"])

        t1_vals = [r[0] for r in results]
        va_vals = [r[1] for r in results]
        vb_vals = [r[2] for r in results]
        pa_vals = [r[3] for r in results]
        pb_vals = [r[4] for r in results]

        # Full coverage counts
        full_cov_a = sum(1 for v in va_vals if v == total_vertices)
        full_cov_b = sum(1 for v in vb_vals if v == total_vertices)

        # Collision time distribution / probability breakdown
        t1_counts = {}
        for t in t1_vals:
            t1_counts[t] = t1_counts.get(t, 0) + 1
        t1_probs = {t: count / total_runs for t, count in t1_counts.items()}

        key_name = f"N{n_verts}_{name.replace(' ', '_')}"
        summary_export[key_name] = {
            "vertex_count": total_vertices,
            "graph_type": name,
            "total_simulations": total_runs,
            "avg_T1": float(np.mean(t1_vals)),
            "avg_distinct_A": float(np.mean(va_vals)),
            "avg_distinct_B": float(np.mean(vb_vals)),
            "avg_percent_A": float(np.mean(pa_vals)),
            "avg_percent_B": float(np.mean(pb_vals)),
            "full_coverage_runs_A": full_cov_a,
            "full_coverage_runs_B": full_cov_b,
            "full_coverage_probability_A": full_cov_a / total_runs,
            "full_coverage_probability_B": full_cov_b / total_runs,
            "collision_time_probabilities": t1_probs
        }

        # Export individual CSV for detailed data inspection
        csv_filename = os.path.join(output_dir, f"results_N{n_verts}_{name.replace(' ', '_')}.csv")
        with open(csv_filename, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Run", "T1", "Distinct_VA", "Distinct_VB", "Percent_A", "Percent_B"])
            for idx, r in enumerate(results, 1):
                writer.writerow([idx, r[0], r[1], r[2], r[3], r[4]])

    # Export master summary JSON
    json_filename = os.path.join(output_dir, "simulation_results_summary.json")
    with open(json_filename, mode="w") as json_file:
        json.dump(summary_export, json_file, indent=4)

    print(f"\n[Export Complete] All results saved successfully in the 'simulation_outputs/' directory.")
    print(f"  - Master Summary: {json_filename}")
    print(f"  - Individual CSVs created for each graph & vertex count combination.\n")


# --------------------------------------------------
# One-window dashboard supporting N = 7, 8, 9, 10
# --------------------------------------------------

class GraphDashboard:
    def __init__(self, master_data):
        self.master_data = master_data
        self.keys = list(master_data.keys())  # list of (n_verts, graph_name)
        self.current_key_index = 0
        self.run_index = 0
        self.view = "traversal"
        self.anim = None
        self.animation_frame = 0

        self.fig = plt.figure(figsize=(13, 8))
        self.fig.canvas.manager.set_window_title("Multi-Size Random Walk Graph Dashboard")

        self.ax_graph = self.fig.add_axes([0.05, 0.19, 0.90, 0.72])
        self.hist_axes = [
            self.fig.add_axes([0.07, 0.56, 0.25, 0.25]),
            self.fig.add_axes([0.38, 0.56, 0.25, 0.25]),
            self.fig.add_axes([0.69, 0.56, 0.25, 0.25]),
            self.fig.add_axes([0.22, 0.20, 0.25, 0.25]),
            self.fig.add_axes([0.53, 0.20, 0.25, 0.25])
        ]

        # Navigation and control buttons
        self.buttons = []
        self._add_button([0.02, 0.08, 0.11, 0.055], "Prev Graph", self.previous_graph)
        self._add_button([0.14, 0.08, 0.11, 0.055], "Next Graph", self.next_graph)
        self._add_button([0.26, 0.08, 0.16, 0.055], "Traversal View", self.show_traversal)
        self._add_button([0.43, 0.08, 0.15, 0.055], "Data / Histogram", self.show_histograms)
        self._add_button([0.59, 0.08, 0.10, 0.055], "Prev Walk", self.previous_walk)
        self._add_button([0.70, 0.08, 0.09, 0.055], "Next Walk", self.next_walk)
        self._add_button([0.80, 0.08, 0.09, 0.055], "Rand Walk", self.random_walk)
        self._add_button([0.90, 0.08, 0.08, 0.055], "Export", self.export_action)

        self._add_button([0.43, 0.015, 0.14, 0.05], "Replay Walk", self.replay_walk)

        self._set_view_visibility()
        self.draw_current_view()
        plt.show()

    def _add_button(self, rect, label, callback):
        ax = self.fig.add_axes(rect)
        button = Button(ax, label)
        button.on_clicked(callback)
        self.buttons.append(button)

    def current_tuple(self):
        return self.keys[self.current_key_index]

    def current_data(self):
        return self.master_data[self.current_tuple()]

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
        self.current_key_index = (self.current_key_index - 1) % len(self.keys)
        self.run_index = 0
        self.animation_frame = 0
        self.draw_current_view()

    def next_graph(self, event):
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
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

    def export_action(self, event):
        export_res = {k: self.master_data[k] for k in self.keys}
        export_results(export_res)

    def draw_traversal(self):
        n_verts, name = self.current_tuple()
        data = self.current_data()
        graph = data["graph"]
        path_a, path_b, T1 = data["paths"][self.run_index]

        G = nx.Graph()
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                G.add_edge(node, neighbor)

        # Clean, scalable layout determination
        if name == "Straight line":
            pos = {node: (node - 1, 0) for node in graph}
        elif name == "Cycle":
            pos = {
                1: (0, 1.5), 2: (1.2, 1), 3: (1.5, -0.2), 4: (0.7, -1.2),
                5: (-0.7, -1.2), 6: (-1.5, -0.2), 7: (-1.2, 1)
            }
        elif name == "Tree T3":
            self.pos = {
                1: (0, 2), 2: (1, 2), 3: (0.8, 1.8), 4: (2, 2),
                5: (3, 2), 6: (3.2, 1.8), 7: (4, 2)
            }
        elif name == "Spider tree 1":
            self.pos = {
                1: (0, 1), 2: (1, 1), 3: (2, 1), 4: (3, 1), 5: (4, 1),
                6: (2, 0), 7: (2, -1)
            }
        elif name == "Spider tree 2":
            self.pos = {
                1: (0, 1), 2: (1, 1), 3: (2, 1), 4: (3, 1), 5: (4, 1),
                6: (3, 0), 7: (3, -1)
            }
        else:
            pos = nx.spring_layout(G, seed=42)

        self.ax_graph.clear()
        self.ax_graph.set_axis_off()

        def update(frame):
            self.animation_frame = frame
            self.ax_graph.clear()
            self.ax_graph.set_axis_off()

            current_a = path_a[frame]
            current_b = path_b[frame]

            nx.draw_networkx_edges(G, pos, width=2, edge_color="gray", ax=self.ax_graph)
            nx.draw_networkx_nodes(G, pos, node_size=650, node_color="lightgray", ax=self.ax_graph)
            nx.draw_networkx_labels(G, pos, font_size=11, font_weight="bold", ax=self.ax_graph)

            if current_a == current_b and frame == T1:
                nx.draw_networkx_nodes(
                    G, pos, nodelist=[current_a], node_size=900,
                    node_color="red", ax=self.ax_graph
                )
                title = (
                    f"[{n_verts} Vertices] {name} | Run {self.run_index + 1}/{len(data['paths'])}\n"
                    f"COLLISION at t = {T1}, node {current_a}"
                )
                self.ax_graph.set_title(title, color="red", fontsize=14, fontweight="bold")
            else:
                colors = []
                sizes = []
                for node in G.nodes():
                    if node == current_a and node == current_b:
                        colors.append("purple")
                        sizes.append(850)
                    elif node == current_a:
                        colors.append("skyblue")
                        sizes.append(750)
                    elif node == current_b:
                        colors.append("orange")
                        sizes.append(750)
                    else:
                        colors.append("lightgray")
                        sizes.append(650)

                nx.draw_networkx_nodes(
                    G, pos, nodelist=list(G.nodes()),
                    node_size=sizes, node_color=colors, ax=self.ax_graph
                )
                self.ax_graph.set_title(
                    f"[{n_verts} Vertices] {name} | Run {self.run_index + 1}/{len(data['paths'])}\n"
                    f"t = {frame}/{T1}   A: node {current_a}   B: node {current_b}",
                    fontsize=13
                )

        self.anim = animation.FuncAnimation(
            self.fig, update, frames=len(path_a), interval=500, repeat=False
        )
        update(min(self.animation_frame, len(path_a) - 1))

    def draw_histograms(self):
        n_verts, name = self.current_tuple()
        data = self.current_data()
        results = data["results"]
        total_vertices = len(data["graph"])

        T_values = [row[0] for row in results]
        A_values = [row[1] for row in results]
        B_values = [row[2] for row in results]
        A_percentages = [row[3] for row in results]
        B_percentages = [row[4] for row in results]

        full_cov_a = sum(1 for v in A_values if v == total_vertices)
        full_cov_b = sum(1 for v in B_values if v == total_vertices)

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
                bins = np.linspace(-100 / (2 * total_vertices), 100 + 100 / (2 * total_vertices), total_vertices + 2)
            else:
                bins = np.arange(min(values) - 0.5, max(values) + 1.5, 1)

            ax.hist(values, bins=bins, edgecolor="black")
            ax.set_title(title, fontsize=10)
            ax.set_xlabel(xlabel, fontsize=9)
            ax.set_ylabel("Frequency", fontsize=9)
            ax.grid(axis="y", alpha=0.3)

        self.fig.suptitle(
            f"Data / Histogram View — [{n_verts} Vertices] {name} "
            f"({len(results)} simulations)",
            fontsize=15
        )

        summary = (
            f"Average T1: {np.mean(T_values):.2f}     "
            f"Average |VA|: {np.mean(A_values):.2f}     "
            f"Average |VB|: {np.mean(B_values):.2f}\n"
            f"Full Coverage A: {full_cov_a}/{len(results)} ({100*full_cov_a/len(results):.2f}%)     "
            f"Full Coverage B: {full_cov_b}/{len(results)} ({100*full_cov_b/len(results):.2f}%)"
        )
        self.fig.text(0.5, 0.145, summary, ha="center", va="center", fontsize=10)

        self.fig.canvas.draw_idle()


# --------------------------------------------------
# Main program
# --------------------------------------------------

def main():
    print(f"=== Graph Traversal Simulation Platform ===")
    print(f"Vertex Counts: {VERTEX_COUNTS}")
    print(f"Simulations per graph: {NUMBER_OF_RUNS}\n")

    master_data = {}

    for n in VERTEX_COUNTS:
        print(f"Generating and simulating graphs for N = {n} vertices...")
        graphs_dict = generate_graphs(n)

        for name, graph in graphs_dict.items():
            (start_a, start_b), distance = find_farthest_vertices(graph)
            results = []
            paths = []

            for _ in range(NUMBER_OF_RUNS):
                T1, number_a, number_b, percent_a, percent_b, path_a, path_b = simulate(graph, start_a, start_b)
                results.append((T1, number_a, number_b, percent_a, percent_b))
                paths.append((path_a, path_b, T1))

            master_data[(n, name)] = {
                "graph": graph,
                "start_a": start_a,
                "start_b": start_b,
                "distance": distance,
                "results": results,
                "paths": paths
            }

    print("\nSimulations complete across all vertex sizes.")
    print("Launching interactive dashboard and exporting results package...")

    # Automatically export results to JSON & CSV on startup
    export_results(master_data)

    # Open unified interactive dashboard
    GraphDashboard(master_data)


if __name__ == "__main__":
    main()