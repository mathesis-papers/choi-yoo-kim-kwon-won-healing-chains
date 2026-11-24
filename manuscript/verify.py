import itertools
import json
from collections import deque


def triangle_tree(height):
    blocks = 3 * 2**height - 2
    children = [[] for block in range(blocks)]
    edges = []
    for block in range(blocks):
        for first, second in itertools.combinations(range(3), 2):
            edges.append((3 * block + first, 3 * block + second))
        candidates = [(port, port + 1) for port in range(3)] if block == 0 else [
            (port, 2 * block + port + 1) for port in (1, 2)
        ]
        for port, child in candidates:
            if child < blocks:
                children[block].append((port, child))
                edges.append((3 * block + port, 3 * child))
    return blocks, children, edges


def independent(selected, edges):
    return all(first not in selected or second not in selected for first, second in edges)


def frustration(children, deleted):
    infinity = 10**12
    costs = [None] * len(children)
    for block in reversed(range(len(children))):
        choices = [(-1,) if 3 * block + port in deleted else (0, 1) for port in range(3)]
        conditional = [infinity, infinity, infinity]
        for coloring in itertools.product(*choices):
            cost = sum(
                coloring[first] == coloring[second] and coloring[first] != -1
                for first, second in itertools.combinations(range(3), 2)
            )
            for port, child in children[block]:
                child_costs = costs[child]
                if coloring[port] == -1 or 3 * child in deleted:
                    cost += min(child_costs)
                else:
                    cost += min(
                        child_costs[color] + (color == coloring[port]) for color in (0, 1)
                    )
            conditional[coloring[0]] = min(conditional[coloring[0]], cost)
        costs[block] = conditional
    return min(costs[0])


def brute_frustration(vertices, edges, deleted):
    remaining = [vertex for vertex in range(vertices) if vertex not in deleted]
    position = {vertex: index for index, vertex in enumerate(remaining)}
    residual = [(position[first], position[second]) for first, second in edges
                if first in position and second in position]
    return min(
        sum(((coloring >> first) & 1) == ((coloring >> second) & 1)
            for first, second in residual)
        for coloring in range(2**len(remaining))
    )


def transversal_cost(children):
    costs = [None] * len(children)
    counts = [None] * len(children)
    for block in reversed(range(len(children))):
        costs[block] = []
        counts[block] = []
        for selected_port in range(3):
            cost = int(block != 0 and selected_port != 0)
            count = 1
            for parent_port, child in children[block]:
                allowed = (1, 2) if selected_port == parent_port else (0, 1, 2)
                cost += min(costs[child][port] for port in allowed)
                count *= sum(counts[child][port] for port in allowed)
            costs[block].append(cost)
            counts[block].append(count)
    return min(costs[0]), sum(counts[0])


def check_height(height):
    blocks, children, edges = triangle_tree(height)
    vertices = 3 * blocks
    neighbors = [set() for vertex in range(vertices)]
    for first, second in edges:
        neighbors[first].add(second)
        neighbors[second].add(first)
    reached = {0}
    queue = deque([0])
    while queue:
        for neighbor in neighbors[queue.popleft()]:
            if neighbor not in reached:
                reached.add(neighbor)
                queue.append(neighbor)
    assert len(reached) == vertices
    assert max(map(len, neighbors)) == 3
    assert len(edges) == 4 * blocks - 1
    apices = {3 * block for block in range(1, blocks)}
    assert len(apices) == blocks - 1 and independent(apices, edges)
    assert all(neighbors[vertex] & apices for vertex in range(vertices) if vertex not in apices)
    assert frustration(children, set()) == blocks
    assert frustration(children, apices) == 1
    minimum, transversals = transversal_cost(children)
    assert minimum == height
    paths = []

    def extend(path):
        if not children[path[-1]]:
            paths.append(path)
        else:
            for port, child in children[path[-1]]:
                extend(path + [child])

    extend([0])
    selected_paths = paths if height <= 5 else paths[:1]
    states = 0
    for path in selected_paths:
        assert len(path) == height + 1
        selected = []
        for parent, child in zip(path, path[1:]):
            port = next(port for port, candidate in children[parent] if candidate == child)
            selected.append(3 * parent + port)
        selected.append(3 * path[-1] + 1)
        current = set(apices)
        for stage in range(height + 1):
            assert independent(current, edges)
            assert len(current) == blocks - 1
            assert len(apices - current) == stage
            assert frustration(children, current) == 1
            free = [vertex for vertex in range(vertices)
                    if vertex not in current and not (neighbors[vertex] & current)]
            assert bool(free) == (stage == height)
            if stage < height:
                current.remove(3 * path[stage + 1])
                current.add(selected[stage])
            states += 1
        augmentation = current | {selected[-1]}
        assert independent(augmentation, edges) and len(augmentation) == blocks
        assert frustration(children, augmentation) == 0
    return {
        'height': height,
        'triangles': blocks,
        'vertices': vertices,
        'edges': len(edges),
        'minimum_displacement': minimum,
        'independent_transversals': transversals,
        'paths_checked': len(selected_paths),
        'exchange_states_checked': states,
    }


def exhaustive_small():
    height = 1
    blocks, children, edges = triangle_tree(height)
    apices = {3 * block for block in range(1, blocks)}
    independent_sets = 0
    augmentable_sets = 0
    best = blocks
    for omitted in range(blocks):
        for ports in itertools.product(range(3), repeat=blocks - 1):
            selected = {3 * block + port for block, port in
                        zip((block for block in range(blocks) if block != omitted), ports)}
            if not independent(selected, edges):
                continue
            independent_sets += 1
            assert brute_frustration(3 * blocks, edges, selected) == 1
            candidates = [selected | {3 * omitted + port} for port in range(3)]
            if any(independent(candidate, edges) for candidate in candidates):
                augmentable_sets += 1
                best = min(best, len(apices - selected))
    assert best == height
    exhaustive_transversals = []
    for height in (1, 2):
        blocks, children, edges = triangle_tree(height)
        best = blocks
        count = 0
        for ports in itertools.product(range(3), repeat=blocks):
            if any(ports[parent] == parent_port and ports[child] == 0
                   for parent in range(blocks) for parent_port, child in children[parent]):
                continue
            count += 1
            best = min(best, sum(port != 0 for port in ports[1:]))
        assert (best, count) == transversal_cost(children)
        exhaustive_transversals.append({'height': height, 'legal_transversals': count,
                                        'minimum_displacement': best})
    return {'height_one_independent_sets_of_size_three': independent_sets,
            'height_one_augmentable_sets_of_size_three': augmentable_sets,
            'height_one_minimum_displacement': 1,
            'exhaustive_transversals': exhaustive_transversals}


def main():
    report = {'schema_version': 1, 'arithmetic': 'exact integers',
              'scope': 'Triangle-tree structure, binary-coloring minima, independent transversals, and explicit exchange paths.',
              'heights': [check_height(height) for height in range(1, 11)],
              'exhaustive': exhaustive_small(), 'status': 'pass'}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
