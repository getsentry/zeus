from collections import defaultdict
from typing import Dict, List, Set


def build_flat_tree(
    tests: List[str], sep: str = ".", min_children: int = 1
) -> Dict[str, Set[str]]:
    tree = defaultdict(set)

    # Build a mapping of prefix => set(children)
    for test in tests:
        segments = test.split(sep)
        for i, _ in enumerate(segments):
            prefix = sep.join(segments[:i + 1])
            tree[prefix].add(test)

    return tree


def build_tree(
    tests: List[str], sep: str = ".", min_children: int = 1, parent: str = ""
) -> Dict[str, Set[str]]:
    tree = defaultdict(set)

    # Build a mapping of prefix => set(children)
    for test in tests:
        segments = test.split(sep)
        for i, _ in enumerate(segments):
            prefix = sep.join(segments[:i])
            tree[prefix].add(sep.join(segments[:i + 1]))

    # This method expands each node if it has fewer than min_children children.
    # "Expand" here means replacing a node with its children.

    def expand(node="", sep=".", min_children=1):
        # Leave leaf nodes alone.
        if node in tree:

            # Expand each child node (depth-first traversal).
            for child in list(tree[node]):
                expand(child, sep, min_children)

            # If this node isn't big enough by itself...
            if len(tree[node]) < min_children and node:
                parent = tree[sep.join(node.split(sep)[:-1])]

                # Replace this node with its expansion.
                parent.remove(node)
                parent.update(tree[node])

                del tree[node]

    # Expand the tree, starting at the root.
    expand(sep=sep, min_children=min_children)

    if parent:
        return tree[parent]

    return tree[""]
