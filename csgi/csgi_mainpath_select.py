import json
import sys
import os
from typing import List, Tuple, Dict, Set, Optional

def get_node_xy(nodes: List[dict], nid: int) -> Tuple[int, int]:
    for n in nodes:
        if n["id"] == nid:
            return (n["x"], n["y"])
    raise ValueError(f"Node {nid} not found")

def get_node_degree(nodes: List[dict], nid: int) -> int:
    for n in nodes:
        if n["id"] == nid:
            return n.get("degree", 0)
    return 0

def find_all_simple_paths(adj: Dict[int, List[int]], start: int, end: int) -> List[List[int]]:
    paths = []
    stack = [(start, [start])]
    while stack:
        (u, path) = stack.pop()
        for v in adj.get(u, []):
            if v == end:
                paths.append(path + [v])
            elif v not in path:
                stack.append((v, path + [v]))
    return paths

def find_all_simple_cycles(adj: Dict[int, List[int]]) -> List[List[int]]:
    cycles = []
    nodes = list(adj.keys())
    for start_node in nodes:
        stack = [(start_node, [start_node])]
        while stack:
            (u, path) = stack.pop()
            for v in adj.get(u, []):
                if v == start_node and len(path) >= 3:
                    # Found a cycle. Normalize to check for duplicates.
                    normalized = sorted(path)
                    if normalized not in [sorted(c) for c in cycles]:
                        cycles.append(path)
                elif v not in path and v > start_node: # Avoid redundant start points
                    stack.append((v, path + [v]))
    return cycles

def get_edge_len(edges: List[dict], u: int, v: int) -> int:
    for e in edges:
        if (e["u"] == u and e["v"] == v) or (e["u"] == v and e["v"] == u):
            return len(e["points"]) - 1
    return 0

def get_path_coords(edges: List[dict], path_nodes: List[int], start_from_small: bool = True) -> List[Tuple[int, int]]:
    coords = []
    nodes_xy = {} # Cache
    
    # Simple case: collect points from edges
    for i in range(len(path_nodes) - 1):
        u, v = path_nodes[i], path_nodes[i+1]
        edge = None
        reverse = False
        for e in edges:
            if e["u"] == u and e["v"] == v:
                edge = e
                reverse = False
                break
            elif e["u"] == v and e["v"] == u:
                edge = e
                reverse = True
                break
        
        pts = edge["points"]
        if reverse:
            pts = pts[::-1]
            
        if i == 0:
            coords.extend([tuple(p) for p in pts])
        else:
            coords.extend([tuple(p) for p in pts[1:]])
            
    return coords

def main():
    if len(sys.argv) < 2:
        print("Usage: python csgi_mainpath_select.py <csgi_file>")
        return

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data["nodes"]
    edges = data["edges"]
    
    adj = {}
    for e in edges:
        u, v = e["u"], e["v"]
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)

    endpoints = [n["id"] for n in nodes if n.get("degree") == 1]
    
    candidates = []
    
    # 1. Open paths between endpoints
    for i in range(len(endpoints)):
        for j in range(i + 1, len(endpoints)):
            paths = find_all_simple_paths(adj, endpoints[i], endpoints[j])
            for p in paths:
                candidates.append({"nodes": p, "closed": 0})
                
    # 2. Closed cycles
    cycles = find_all_simple_cycles(adj)
    for c in cycles:
        candidates.append({"nodes": c + [c[0]], "closed": 1})

    # Pre-calculate cycle edges
    cycle_edges = set()
    for c in cycles:
        for i in range(len(c)):
            u, v = c[i], c[(i+1)%len(c)]
            cycle_edges.add(tuple(sorted((u, v))))

    scored_candidates = []
    for cand in candidates:
        p_nodes = cand["nodes"]
        
        # Length
        length = 0
        for i in range(len(p_nodes) - 1):
            length += get_edge_len(edges, p_nodes[i], p_nodes[i+1])
            
        # Junctions
        junc_count = 0
        # Passing through junctions. Endpoints might be junctions in some weird graphs, 
        # but usually degree >= 3.
        # User says: "A, B, C adalah junction; D degree 2."
        for nid in p_nodes:
            if get_node_degree(nodes, nid) >= 3:
                junc_count += 1
                
        # Closed
        closed = cand["closed"]
        
        # Coverage
        cov = 0
        for i in range(len(p_nodes) - 1):
            pair = tuple(sorted((p_nodes[i], p_nodes[i+1])))
            if pair in cycle_edges:
                cov += get_edge_len(edges, p_nodes[i], p_nodes[i+1])
                
        # Score S = (Len, -Junc, Closed, Cov)
        score = (length, -junc_count, closed, cov)
        
        # EmbKey for tie-break
        # Orient path: start node coord must be lexically smaller than end node coord
        path_coords = get_path_coords(edges, p_nodes)
        
        # For open paths, we might need to reverse to get canonical form
        if not closed:
            start_coord = path_coords[0]
            end_coord = path_coords[-1]
            if start_coord > end_coord:
                # Reverse the node path and re-get coords
                p_nodes_rev = p_nodes[::-1]
                path_coords = get_path_coords(edges, p_nodes_rev)
        else:
            # For closed cycles, find the smallest coord and start there
            min_idx = 0
            min_val = path_coords[0]
            for i in range(1, len(path_coords) - 1): # Exclude last since it's same as first
                if path_coords[i] < min_val:
                    min_val = path_coords[i]
                    min_idx = i
            
            # Two directions
            c1 = path_coords[min_idx:-1] + path_coords[:min_idx+1]
            # Reverse direction
            rev_coords = path_coords[::-1] # F...D...A...B...F
            # Find min_idx in rev_coords (might be different index but same value)
            # Actually easier to just reverse c1 and compare
            c2 = c1[0:1] + c1[1:][::-1]
            path_coords = min(c1, c2)

        scored_candidates.append({
            "nodes": p_nodes,
            "score": score,
            "emb_key": path_coords,
            "closed": closed
        })

    # Sort candidates by score descending, then emb_key ascending
    # Python sort is stable.
    # Score is (Len, -Junc, Closed, Cov)
    # We want max(Len), then max(-Junc) which is min(Junc), then max(Closed), then max(Cov)
    # Then min(EmbKey)
    
    # Custom sort key
    def sort_key(x):
        return (x["score"][0], x["score"][1], x["score"][2], x["score"][3])

    # Sort by score descending
    scored_candidates.sort(key=sort_key, reverse=True)
    
    # Handle ties with EmbKey
    final_candidates = []
    if scored_candidates:
        top_score = scored_candidates[0]["score"]
        ties = [c for c in scored_candidates if c["score"] == top_score]
        ties.sort(key=lambda x: x["emb_key"])
        winner = ties[0]
        
        winner_str = "-".join(map(str, winner['nodes']))
        print(f"Winner: {winner_str}")
        print(f"Score: Len={winner['score'][0]}, Junc={-winner['score'][1]}, Closed={winner['score'][2]}, Cov={winner['score'][3]}")
        
        # Regression Test Assertion
        expected = data.get("expected_winner")
        if expected:
            if winner_str == expected:
                print("REGRESSION TEST: PASS")
            else:
                print(f"REGRESSION TEST: FAIL (Expected {expected}, got {winner_str})")
                sys.exit(1)
        
        # Output top 10 candidates for audit
        print("\nTop 10 Candidates (Audit):")
        for idx, c in enumerate(scored_candidates[:10]):
            path_str = " -> ".join(map(str, c['nodes']))
            print(f"{idx+1}. {path_str} | Score: {c['score']}")

if __name__ == "__main__":
    main()
