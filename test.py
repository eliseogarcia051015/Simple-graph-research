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

def _adjacency_from_edges(vertices, edges):
    """Build a symmetric adjacency dictionary from an edge list."""
    graph = {v: [] for v in vertices}
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    return {v: sorted(neighbors) for v, neighbors in graph.items()}


def _extend_tree_from_alternating_ends(graph, n, end_vertices):
    """Add new vertices by extending alternating, opposing terminal arms."""
    graph = {v: list(neighbors) for v, neighbors in graph.items()}
    next_vertex = 8
    side_index = 0

    while len(graph) < n:
        leaf = end_vertices[side_index % len(end_vertices)]
        new_vertex = next_vertex
        graph[leaf].append(new_vertex)
        graph[new_vertex] = [leaf]
        end_vertices[side_index % len(end_vertices)] = new_vertex
        next_vertex += 1
        side_index += 1

    return {v: sorted(neighbors) for v, neighbors in graph.items()}


def _extend_cycle(n):
    """Subdivide alternating, separated edges of the original 7-cycle."""
    order = [1, 2, 3, 4, 5, 6, 7]
    # Insert the first new vertex on one side, the second on the opposite side.
    # Further vertices continue around the cycle in a spaced-out pattern.
    insertion_edges = [(7, 1), (3, 4), (5, 6)]

    for new_vertex, (u, v) in enumerate(insertion_edges, start=8):
        if new_vertex > n:
            break
        index = order.index(u)
        if order[(index + 1) % len(order)] != v:
            raise ValueError("Cycle extension edge is not consecutive.")
        order.insert(index + 1, new_vertex)

    edges = [(order[i], order[(i + 1) % len(order)]) for i in range(len(order))]
    return _adjacency_from_edges(order, edges), order


def generate_graphs(n):
    """Generate the five original 7-vertex graphs, extending their arms for n>7.

    The original vertices and edges are preserved. Tree extensions are added
    alternately to opposing terminal arms; cycle extensions subdivide separated
    edges; path extensions alternate between its two endpoints.
    """
    if n < 7 or n > 10:
        raise ValueError("This graph family supports 7 through 10 vertices.")

    # T1: the exact tree supplied by the user.
    T1 = _adjacency_from_edges(
        range(1, 8),
        [(1, 2), (2, 3), (3, 4), (4, 5), (3, 6), (6, 7)]
    )
    T1 = _extend_tree_from_alternating_ends(T1, n, [1, 5])

    # T2: the exact three-armed spider supplied by the user.
    T2 = _adjacency_from_edges(
        range(1, 8),
        [(1, 2), (2, 3), (3, 4), (4, 5), (4, 6), (6, 7)]
    )
    T2 = _extend_tree_from_alternating_ends(T2, n, [1, 7])

    # P: straight path. New vertices are added to opposite endpoints in turn.
    path_order = [1, 2, 3, 4, 5, 6, 7]
    left_end, right_end = 1, 7
    for new_vertex in range(8, n + 1):
        if new_vertex % 2 == 0:
            path_order.insert(0, new_vertex)
            left_end = new_vertex
        else:
            path_order.append(new_vertex)
            right_end = new_vertex
    P = _adjacency_from_edges(
        path_order,
        [(path_order[i], path_order[i + 1]) for i in range(len(path_order) - 1)]
    )

    # C: cycle, extended by subdividing separated edges rather than changing
    # the original cycle into a different graph.
    C, cycle_order = _extend_cycle(n)

    # T3 / Tree T4: the exact two-branching-vertex tree supplied by the user.
    T3 = _adjacency_from_edges(
        range(1, 8),
        [(1, 2), (2, 3), (2, 4), (4, 5), (5, 6), (5, 7)]
    )
    T3 = _extend_tree_from_alternating_ends(T3, n, [1, 7])

    return {
        "Spider tree 1": T1,
        "Spider tree 2": T2,
        "Straight line": P,
        "Cycle": C,
        "Tree T4": T3
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
        self.keys = list(master_data.keys())
        self.current_key_index = 0
        self.run_index = 0
        self.view = "traversal"
        self.anim = None
        self.animation_frame = 0
        self.summary_text = None

        self.fig = plt.figure(figsize=(13, 8))
        self.fig.canvas.manager.set_window_title(
            "Multi-Size Random Walk Graph Dashboard"
        )

        self.ax_graph = self.fig.add_axes([0.05, 0.19, 0.90, 0.72])
        self.hist_axes = [
            self.fig.add_axes([0.07, 0.56, 0.25, 0.25]),
            self.fig.add_axes([0.38, 0.56, 0.25, 0.25]),
            self.fig.add_axes([0.69, 0.56, 0.25, 0.25]),
            self.fig.add_axes([0.22, 0.20, 0.25, 0.25]),
            self.fig.add_axes([0.53, 0.20, 0.25, 0.25])
        ]

        # Keep references to every button so their callbacks remain active.
        self.buttons = []
        self._add_button(
            [0.02, 0.08, 0.11, 0.055], "Prev Graph", self.previous_graph
        )
        self._add_button(
            [0.14, 0.08, 0.11, 0.055], "Next Graph", self.next_graph
        )

        # One button toggles between traversal and histogram views.
        self.view_button = self._add_button(
            [0.26, 0.08, 0.20, 0.055], "Histogram", self.toggle_view
        )

        self._add_button(
            [0.48, 0.08, 0.10, 0.055], "Prev Walk", self.previous_walk
        )
        self._add_button(
            [0.59, 0.08, 0.10, 0.055], "Next Walk", self.next_walk
        )
        self._add_button(
            [0.70, 0.08, 0.09, 0.055], "Rand Walk", self.random_walk
        )
        self._add_button(
            [0.80, 0.08, 0.09, 0.055], "Export", self.export_action
        )
        self._add_button(
            [0.43, 0.015, 0.14, 0.05], "Replay Walk", self.replay_walk
        )

        self.draw_current_view()
        plt.show()

    def _add_button(self, rect, label, callback):
        ax = self.fig.add_axes(rect)
        button = Button(ax, label)
        button.on_clicked(callback)
        self.buttons.append(button)
        return button

    def current_tuple(self):
        return self.keys[self.current_key_index]

    def current_data(self):
        return self.master_data[self.current_tuple()]

    def _stop_animation(self):
        if self.anim is not None:
            if self.anim.event_source is not None:
                self.anim.event_source.stop()
            self.anim = None

    def _remove_summary_text(self):
        if self.summary_text is not None:
            try:
                self.summary_text.remove()
            except ValueError:
                pass
            self.summary_text = None

    def _clear_view_artists(self):
        """Remove content belonging to the previous view before drawing."""
        self._remove_summary_text()
        self.fig.suptitle("")

        self.ax_graph.clear()
        for ax in self.hist_axes:
            ax.clear()

    def _update_view_button(self):
        # The label describes the view the button will switch TO.
        if self.view == "traversal":
            self.view_button.label.set_text("Histogram")
        else:
            self.view_button.label.set_text("Graph View")

    def draw_current_view(self):
        self._stop_animation()
        self._clear_view_artists()
        self._update_view_button()

        if self.view == "traversal":
            self.ax_graph.set_visible(True)
            for ax in self.hist_axes:
                ax.set_visible(False)
            self.draw_traversal()
        else:
            self.ax_graph.set_visible(False)
            for ax in self.hist_axes:
                ax.set_visible(True)
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

    def toggle_view(self, event):
        if self.view == "traversal":
            self.view = "histograms"
        else:
            self.view = "traversal"

        self.animation_frame = 0
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
        export_results(self.master_data)

    def _make_graph_and_layout(self, graph, name):
        G = nx.Graph()
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                G.add_edge(node, neighbor)

        n = len(graph)

        if name == "Straight line":
            # Keep original vertices 1..7 in their original order. Extra
            # vertices extend alternately from the left and right ends.
            order = []
            left = 1
            right = 7
            # Recover the unique path from an endpoint, then place it straight.
            endpoints = [v for v in G.nodes() if G.degree(v) == 1]
            current = endpoints[0]
            previous = None
            while True:
                order.append(current)
                following = [v for v in G.neighbors(current) if v != previous]
                if not following:
                    break
                previous, current = current, following[0]
            pos = {node: (i, 0) for i, node in enumerate(order)}

        elif name == "Cycle":
            # Follow the cycle in label order, including inserted vertices.
            start = 1
            order = [start]
            previous = None
            current = start
            while True:
                candidates = [v for v in G.neighbors(current) if v != previous]
                following = min(candidates) if len(order) == 1 else candidates[0]
                if following == start:
                    break
                order.append(following)
                previous, current = current, following
            # The walk above may choose either direction; a circular layout
            # preserves the cycle shape regardless of which direction is used.
            angles = np.linspace(np.pi / 2, np.pi / 2 - 2 * np.pi, len(order), endpoint=False)
            pos = {
                node: (1.8 * np.cos(angle), 1.8 * np.sin(angle))
                for node, angle in zip(order, angles)
            }

        else:
            # Exact hand-positioned layouts for the seven original vertices.
            if name == "Spider tree 1":  # T1
                pos = {
                    1: (-3, 0), 2: (-2, 0), 3: (-1, 0),
                    4: (0, 0), 5: (1, 0), 6: (-1, -1), 7: (-1, -2)
                }
            elif name == "Spider tree 2":  # T2
                pos = {
                    1: (-3, 0), 2: (-2, 0), 3: (-1, 0), 4: (0, 0),
                    5: (0, -1), 6: (1, 0), 7: (2, 0)
                }
            elif name == "Tree T4":  # T3
                 pos = {
                    1: (0, 2), 2: (1, 2), 3: (0.8, 1.8), 4: (2, 2),
                    5: (3, 2), 6: (3.2, 1.8), 7: (4, 2)
                }
            else:
                raise ValueError(f"Unknown graph type: {name}")

            # Extend each selected terminal arm in the same direction as its
            # existing final edge. This keeps the original shape recognizable.
            for node in sorted(set(G.nodes()) - set(pos)):
                parent = next(iter(G.neighbors(node)))
                grandparent_candidates = [v for v in G.neighbors(parent) if v != node]
                if grandparent_candidates:
                    grandparent = grandparent_candidates[0]
                    dx = pos[parent][0] - pos[grandparent][0]
                    dy = pos[parent][1] - pos[grandparent][1]
                    length = (dx * dx + dy * dy) ** 0.5
                    if length == 0:
                        dx, dy, length = 1, 0, 1
                    pos[node] = (pos[parent][0] + dx / length,
                                pos[parent][1] + dy / length)
                else:
                    pos[node] = (pos[parent][0] + 1, pos[parent][1])

        missing = set(G.nodes()) - set(pos)
        if missing:
            raise ValueError(f"Missing graph positions for vertices: {sorted(missing)}")

        return G, pos

    def draw_traversal(self):
        n_verts, name = self.current_tuple()
        data = self.current_data()
        path_a, path_b, T1 = data["paths"][self.run_index]
        G, pos = self._make_graph_and_layout(data["graph"], name)

        def update(frame):
            # A callback from an old animation should never redraw a new view.
            if self.view != "traversal":
                return

            self.animation_frame = frame
            self.ax_graph.clear()
            self.ax_graph.set_axis_off()

            current_a = path_a[frame]
            current_b = path_b[frame]

            nx.draw_networkx_edges(
                G, pos, width=2, edge_color="gray", ax=self.ax_graph
            )
            nx.draw_networkx_labels(
                G, pos, font_size=11, font_weight="bold", ax=self.ax_graph
            )

            if current_a == current_b and frame == T1:
                nx.draw_networkx_nodes(
                    G, pos, nodelist=[current_a], node_size=900,
                    node_color="red", ax=self.ax_graph
                )
                self.ax_graph.set_title(
                    f"[{n_verts} Vertices] {name} | "
                    f"Run {self.run_index + 1}/{len(data['paths'])}\n"
                    f"COLLISION at t = {T1}, node {current_a}",
                    color="red", fontsize=14, fontweight="bold"
                )
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
                    f"[{n_verts} Vertices] {name} | "
                    f"Run {self.run_index + 1}/{len(data['paths'])}\n"
                    f"t = {frame}/{T1}   A: node {current_a}   B: node {current_b}",
                    fontsize=13
                )

        # Draw the selected walk immediately, then animate it.
        update(min(self.animation_frame, len(path_a) - 1))

        remaining_frames = range(self.animation_frame + 1, len(path_a))
        if len(remaining_frames) > 0:
            self.anim = animation.FuncAnimation(
                self.fig,
                update,
                frames=remaining_frames,
                interval=500,
                repeat=False,
                blit=False,
                cache_frame_data=False
            )

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

        full_cov_a = sum(1 for value in A_values if value == total_vertices)
        full_cov_b = sum(1 for value in B_values if value == total_vertices)

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
                bins = np.linspace(
                    -100 / (2 * total_vertices),
                    100 + 100 / (2 * total_vertices),
                    total_vertices + 2
                )
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
            f"Full Coverage A: {full_cov_a}/{len(results)} "
            f"({100 * full_cov_a / len(results):.2f}%)     "
            f"Full Coverage B: {full_cov_b}/{len(results)} "
            f"({100 * full_cov_b / len(results):.2f}%)"
        )
        self.summary_text = self.fig.text(
            0.5, 0.145, summary, ha="center", va="center", fontsize=10
        )


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