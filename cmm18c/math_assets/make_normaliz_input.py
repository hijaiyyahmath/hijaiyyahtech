# Converts 4ti2 matrix file A (row-wise: r x m) into Normaliz generators (m lines, each dim=r).
# Input A format:
#   first line: "r m"
#   next r lines: each has m integers
# Output generators.txt: m lines, each has r integers (columns of A).

import sys

A_path = sys.argv[1]
out_path = sys.argv[2]

with open(A_path, "r", encoding="utf-8") as f:
    first = f.readline().strip().split()
    r, m = int(first[0]), int(first[1])
    rows = []
    for _ in range(r):
        line = f.readline().strip()
        if not line:
            raise ValueError("Unexpected EOF while reading matrix A.")
        rows.append(list(map(int, line.split())))

# columns as generators
cols = []
for j in range(m):
    cols.append([rows[i][j] for i in range(r)])

with open(out_path, "w", encoding="utf-8") as g:
    for c in cols:
        g.write(" ".join(map(str, c)) + "\n")