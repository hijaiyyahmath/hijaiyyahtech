import cv2, numpy as np, networkx as nx, sys, os
from skimage.morphology import skeletonize
from generate_st28_full import extract_trace, svg_to_png

# Direct check of Jeem
svg_path = "Hijaiyah Glyph/Arabic_letter_Jeem.svg"
png_path = "_debug_jeem.png"

print(f"Converting {svg_path} -> {png_path}")
svg_to_png(svg_path, png_path, target_size=1200)

print("Extracting trace...")
# We use the internal functions to get tokens before normalization
# Import internals
from generate_st28_full import (
    binarize_inv, remove_long_hlines, split_body_nuq, bbox,
    skel_graph, mainpath, trace_from_path, normalize_vortex,
    find_best_path
)

gray = cv2.imread(png_path, cv2.IMREAD_GRAYSCALE)
fg = binarize_inv(gray)
fg = remove_long_hlines(fg)
body, nuq = split_body_nuq(fg)
x0,y0,x1,y1 = bbox(body)
body_c = body[y0:y1+1, x0:x1+1]

sk, G = skel_graph(body_c)
print(f"Skeleton graph: {len(G.nodes)} nodes, {len(G.edges)} edges")

# Analyze graph endpoints
endpoints = [n for n in G.nodes() if G.degree(n) == 1]
print(f"Endpoints: {len(endpoints)} -> {endpoints}")

path = find_best_path(G, "ج")
print(f"Main path length: {len(path)} nodes")

tokens = trace_from_path(path, smooth=False)
print("\n--- Raw Tokens (Turns, No Smooth) ---")
turns = [t for t in tokens if "TURN" in t]
print(turns)

norm_tokens = normalize_vortex(tokens)
print("\n--- Normalized Tokens ---")
print([t for t in norm_tokens if "TURN" in t or "VORTEX" in t])

# Visualize skeleton and path
h, w = body_c.shape
vis = np.zeros((h, w, 3), dtype=np.uint8)
# Draw skeleton (white)
for (x,y) in G.nodes:
    vis[y, x] = [255, 255, 255]
# Draw path (red)
for (x,y) in path:
    # Handle float coordinates from smooth/repair
    ix, iy = int(x), int(y)
    if 0 <= ix < w and 0 <= iy < h:
        vis[iy, ix] = [0, 0, 255] # BGR -> Red

# Print path endpoints
if path:
    print(f"Path Start: {path[0]}")
    print(f"Path End:   {path[-1]}")
    # Also first 20 points
    print(f"First 20: {path[:20]}")
