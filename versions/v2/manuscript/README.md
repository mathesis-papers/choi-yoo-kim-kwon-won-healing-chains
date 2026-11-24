# Exact healing displacement on triangle trees

**Unbounded healing chains in the question of Choi, Yoo, Kim, Kwon and Won**  
Haobo Ma — ChronoAI Pte Ltd, Singapore  
Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore  
November 17, 2026 · Revision 2 · CC BY 4.0

## Results

For a full rooted triangle tree, the minimum displacement from the nonroot-apex set to an augmentable tight set of equal cardinality is exactly the shortest root-to-leaf distance. This is also the minimum number of tight single-vertex exchanges. The uniform height-h tree has `9*2^h - 6` vertices and distance h; these graphs are outerplanar, subcubic and of treewidth two. Within the stated tree class, this is the smallest order for shortest leaf depth h.

The first successful tested exchange in the chain procedure has minimum zero-based stage index h - 1 on the uniform family. For an arbitrary bridge-connected tree of triangles, every optimal two-colouring is healable: one endpoint of each monochromatic edge can be chosen independently. This last assertion does not require a degree bound.

The posing question is in Choi, Yoo, Kim, Kwon and Won, arXiv:2610.41277v1, Section VIII, Open problems (1), printed page 7. Proposition 15 spans pages 10–11; Corollary 16 is on page 11. The note distinguishes that question from positive optimal-transversal identities and reconfiguration between two full independent transversals. Its coverage table identifies the other source questions and the prior answer to the cross-referenced independent-deletion threshold problem.

## Build the PDF

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively use a standard LaTeX installation with the packages named in the preamble:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is embedded in `note.tex`; no separate bibliography file or BibTeX step is required.

## Exact finite computations

Both programs use the Python 3 standard library and exact integer arithmetic:

```sh
python3 verify.py > checks-reproduced.json
python3 verify_siblings.py > sibling-checks-reproduced.json
cmp checks.json checks-reproduced.json
cmp sibling-checks.json sibling-checks-reproduced.json
```

`verify.py` checks uniform heights 1–10, up to 9,210 vertices. It computes binary-colouring minima and independent-transversal costs by tree dynamic programming and checks 525 exchange states. Every root-to-leaf path is included through height 5; one path is included at each larger height. Separate exhaustive enumerations cover the 90 independent sets of size three at height 1 (89 are augmentable), all 54 independent transversals at height 1 and all 15,876 at height 2.

`verify_siblings.py` enumerates all 428 ordered full rooted trees with 4, 6, 8, 10, 12 or 14 triangles. It checks the shortest-leaf displacement, the order bound, 3,234 root-to-leaf paths and 12,558 exchange states. An independent exhaustive enumeration of all 4,096 binary colourings of the 12-vertex height-one graph finds 162 optimal colourings and constructs a healing choice for each.

The finite computations supplement the written proofs for all finite trees; they are not substitutes for those proofs.

## Formal statement

The pinned file is:

https://github.com/the-omega-institute/trureturing/blob/0ad94071772b2f32b432905d088bfce029d8d29e/D5/S3/Combinatorics/Graph/Potts/HealingUnbounded.lean

Its declaration `D5.S3.Combinatorics.Graph.Potts.HealingUnbounded.result` has statement `¬ claim`: there is no uniform natural-number displacement bound for finite connected subcubic graphs other than K4, from stuck tight sets with positive residual frustration to augmentable tight sets of the same cardinality. The exact shortest-leaf formula, sharp attaining sequences, outerplanarity, treewidth, independent-deletion identity, chain-stage interpretation and universal healability for triangle trees have written proofs in the note.

## Source files and license

The source archive contains `note.tex`, this README, `metadata.json`, both Python programs, their two expected JSON outputs, and `SHA256SUMS`. The programs require no downloaded data. All six bibliographic entries appear in the note with primary-source links.

Copyright 2026 Haobo Ma and Wenlin Zhang. Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0), identifier `cc-by-4.0`.
