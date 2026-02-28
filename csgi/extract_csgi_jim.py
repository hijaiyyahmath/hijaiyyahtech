import cv2
import numpy as np
import networkx as nx
import json
import os
from skimage.morphology import skeletonize
from generate_st28_full import (
    svg_to_png, binarize_inv, remove_long_hlines, split_body_nuq, 
    bbox, skel_graph
)

def extract_csgi_jim():
    svg_path = "Hijaiyah Glyph/Arabic_letter_Jeem.svg"
    png_path = "_jim_temp.png"
    
    # 1. Image Preprocessing
    print(f"Converting {svg_path} -> {png_path}")
    svg_to_png(svg_path, png_path, target_size=1200)
    
    gray = cv2.imread(png_path, cv2.IMREAD_GRAYSCALE)
    fg = binarize_inv(gray)
    fg = remove_long_hlines(fg)
    body, nuq = split_body_nuq(fg)
    
    # Crop to body to normalize coordinates
    x0, y0, x1, y1 = bbox(body)
    body_c = body[y0:y1+1, x0:x1+1]
    # Keep nuq relative to the same bounding box
    nuq_c = nuq[y0:y1+1, x0:x1+1]
    
    # 2. Skeletonization
    sk, G = skel_graph(body_c)
    
    # 3. Node/Edge decomposition for CSGI-1.0
    # Identify nodes: endpoints (deg 1) or junctions (deg >= 3)
    # Kinks are deg 2 but might be necessary if they define sharp turns
    # For now, let's treat any non-deg-2 path segment endpoint as a node.
    
    nodes_data = []
    node_map = {} # (x,y) -> id
    
    # junctions and endpoints
    critical_pts = [n for n in G.nodes if G.degree[n] != 2]
    
    # If a path is a pure cycle, we need at least one node
    if not critical_pts and G.nodes:
        critical_pts = [list(G.nodes)[0]]
        
    for i, pt in enumerate(critical_pts, 1):
        x, y = pt
        deg = G.degree[pt]
        kind = "junction" if deg >= 3 else "endpoint"
        nodes_data.append({
            "id": i,
            "x": int(x),
            "y": int(y),
            "kind": kind,
            "degree": deg
        })
        node_map[pt] = i
        
    edges_data = []
    edge_id = 1
    
    # Traverse paths between critical nodes
    visited_edges = set()
    for u in critical_pts:
        for v in G.neighbors(u):
            if tuple(sorted((u, v))) in visited_edges:
                continue
                
            # Follow the path until we hit another critical node
            path = [u, v]
            curr = v
            prev = u
            while curr not in critical_pts:
                neighbors = list(G.neighbors(curr))
                next_node = [n for n in neighbors if n != prev][0]
                path.append(next_node)
                prev = curr
                curr = next_node
            
            target = curr
            visited_edges.add(tuple(sorted((u, v))))
            # Need to mark all edges in this segment as visited if they exist in G
            # But simple simple graph, one segment = one CSGI edge usually
            # Actually we need to mark all micro-edges in this path
            for i in range(len(path)-1):
                visited_edges.add(tuple(sorted((path[i], path[i+1]))))
                
            edges_data.append({
                "id": edge_id,
                "u": node_map[u],
                "v": node_map[target],
                "points": [[int(px), int(py)] for px, py in path]
            })
            edge_id += 1

    # Recalculate degrees based on actual unique neighbors in edges_data
    node_neighbors = {}
    for e in edges_data:
        u, v = e["u"], e["v"]
        node_neighbors.setdefault(u, set()).add(v)
        node_neighbors.setdefault(v, set()).add(u)
    
    for n in nodes_data:
        if n["id"] in node_neighbors:
            n["degree"] = len(node_neighbors[n["id"]])
        elif n["kind"] == "nuqṭah":
            n["degree"] = 0
        else:
            # Maybe an isolated node? Should keep original degree if any
            pass

    # 4. Handle Nuqṭah (body-relative)
    # Jim has one nuqṭah (nm)
    num, lbl, stats, _ = cv2.connectedComponentsWithStats(nuq_c, connectivity=8)
    for i in range(1, num):
        stat = stats[i]
        # centroid
        nx_c = int(stat[cv2.CC_STAT_LEFT] + stat[cv2.CC_STAT_WIDTH] / 2)
        ny_c = int(stat[cv2.CC_STAT_TOP] + stat[cv2.CC_STAT_HEIGHT] / 2)
        
        nid = len(nodes_data) + 1
        nodes_data.append({
            "id": nid,
            "x": nx_c,
            "y": ny_c,
            "kind": "nuqṭah",
            "degree": 0
        })

    # 5. Format JSON
    csgi = {
        "csgi_version": "CSGI-1.0",
        "letter": "ج",
        "embedding": {
            "coord_system": "raster",
            "axis_convention": "x_right_y_down",
            "units": "px",
            "bbox_body": [0, 0, int(body_c.shape[1]), int(body_c.shape[0])],
            "resolution": [int(body_c.shape[1]), int(body_c.shape[0])],
            "origin": [0, 0]
        },
        "nodes": nodes_data,
        "edges": edges_data,
        "meta": {
            "dataset_seal_id": "MH-28-v1.0-18D",
            "adjacency": "8-neighborhood",
            "notes": "Original Jim CSGI extracted from SVG source."
        }
    }
    
    with open("CSGI_jim.json", "w", encoding="utf-8") as f:
        json.dump(csgi, f, ensure_ascii=False, indent=2)
    print("Saved CSGI_jim.json")

if __name__ == "__main__":
    extract_csgi_jim()
