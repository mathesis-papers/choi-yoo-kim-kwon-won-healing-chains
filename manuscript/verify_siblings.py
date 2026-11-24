import functools
import itertools
import json

import verify


@functools.lru_cache(None)
def binary_shapes(internal_nodes):
    if internal_nodes == 0:
        return ((),)
    return tuple(
        (left, right)
        for left_size in range(internal_nodes)
        for left in binary_shapes(left_size)
        for right in binary_shapes(internal_nodes - left_size - 1)
    )


def rooted_shapes(extra_internal_nodes):
    for first_size in range(extra_internal_nodes + 1):
        for second_size in range(extra_internal_nodes - first_size + 1):
            third_size = extra_internal_nodes - first_size - second_size
            yield from itertools.product(binary_shapes(first_size),
                                         binary_shapes(second_size),
                                         binary_shapes(third_size))


def triangle_tree(shape):
    children = []

    def append(subtree, is_root=False):
        block = len(children)
        children.append([])
        ports = range(3) if is_root else (1, 2)
        for port, child_shape in zip(ports, subtree):
            child = append(child_shape)
            children[block].append((port, child))
        return block

    append(shape, True)
    edges = [(3 * block + first, 3 * block + second)
             for block in range(len(children))
             for first, second in itertools.combinations(range(3), 2)]
    edges += [(3 * block + port, 3 * child)
              for block, descendants in enumerate(children)
              for port, child in descendants]
    return children, edges


def paths_from_root(children):
    paths = []

    def append(path):
        if not children[path[-1]]:
            paths.append(path)
        for port, child in children[path[-1]]:
            append(path + [child])

    append([0])
    return paths


def check_shape(shape):
    children, edges = triangle_tree(shape)
    blocks = len(children)
    apices = {3 * block for block in range(1, blocks)}
    paths = paths_from_root(children)
    distance = min(len(path) - 1 for path in paths)
    assert verify.transversal_cost(children)[0] == distance
    assert blocks + 2 >= 3 * 2**distance
    assert verify.frustration(children, set()) == blocks
    assert verify.frustration(children, apices) == 1
    neighbors = [set() for vertex in range(3 * blocks)]
    for first, second in edges:
        neighbors[first].add(second)
        neighbors[second].add(first)
    states = 0
    for path in paths:
        selected = set(apices)
        for stage, block in enumerate(path):
            assert verify.independent(selected, edges)
            assert len(selected) == blocks - 1
            assert len(apices - selected) == stage
            assert verify.frustration(children, selected) == 1
            free = [vertex for vertex in range(3 * blocks)
                    if vertex not in selected and not (neighbors[vertex] & selected)]
            assert bool(free) == (stage == len(path) - 1)
            states += 1
            if stage < len(path) - 1:
                child = path[stage + 1]
                port = next(port for port, candidate in children[block] if candidate == child)
                selected.remove(3 * child)
                selected.add(3 * block + port)
            else:
                assert verify.frustration(children, selected | {free[0]}) == 0
    return blocks, distance, len(paths), states


def healable_witness(coloring, children):
    selected = set()
    forbidden = set()
    for block, descendants in enumerate(children):
        monochromatic = [(first, second)
                         for first, second in itertools.combinations(range(3), 2)
                         if coloring[3 * block + first] == coloring[3 * block + second]]
        assert len(monochromatic) == 1
        candidates = [3 * block + port for port in monochromatic[0]
                      if 3 * block + port not in forbidden]
        assert candidates
        chosen = min(candidates)
        selected.add(chosen)
        for port, child in descendants:
            if chosen == 3 * block + port:
                forbidden.add(3 * child)
    return selected


def exhaustive_healability():
    blocks, children, edges = verify.triangle_tree(1)
    checked = 0
    for coloring in itertools.product((0, 1), repeat=3 * blocks):
        if sum(coloring[first] == coloring[second] for first, second in edges) != blocks:
            continue
        selected = healable_witness(coloring, children)
        assert len(selected) == blocks and verify.independent(selected, edges)
        assert all((first in selected) + (second in selected) == 1
                   for first, second in edges if coloring[first] == coloring[second])
        checked += 1
    assert checked == 162
    return {'vertices': 3 * blocks, 'binary_colorings_enumerated': 2**(3 * blocks),
            'optimal_colorings': checked, 'healable_colorings': checked}


def main():
    rows = []
    for extra_internal_nodes in range(6):
        cases = [check_shape(shape) for shape in rooted_shapes(extra_internal_nodes)]
        rows.append({'triangles': 4 + 2 * extra_internal_nodes,
                     'ordered_trees': len(cases),
                     'shortest_leaf_depths': sorted({case[1] for case in cases}),
                     'paths_checked': sum(case[2] for case in cases),
                     'exchange_states_checked': sum(case[3] for case in cases)})
    report = {'schema_version': 1, 'arithmetic': 'exact integers',
              'scope': 'All ordered full rooted triangle trees with 4 through 14 triangles; exact shortest-leaf displacement, deletion identities along each root-to-leaf exchange path, and exhaustive small-graph healability.',
              'tree_families': rows, 'ordered_trees_checked': sum(row['ordered_trees'] for row in rows),
              'exhaustive_healability': exhaustive_healability(), 'status': 'pass'}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
