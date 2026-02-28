import cv2
import numpy as np
import networkx as nx
from skimage.morphology import skeletonize
import argparse
import json

# ================== SPEC LOCKS v0.1 ==================
DIR_MAP = {
    ( 1, 0): ("D0",0), ( 1,-1): ("D1",1), ( 0,-1): ("D2",2), (-1,-1): ("D3",3),
    (-1, 0): ("D4",4), (-1, 1): ("D5",5), ( 0, 1): ("D6",6), ( 1, 1): ("D7",7),
}

# DIR_AXIS_MAP (fixed)
DIR_AXIS = [0,9,2,10,4,1,3,8]  # D0..D7 -> axis index

def signed_delta(a,b):
    d = b - a
    if d > 4: d -= 8
    if d < -4: d += 8
    return d

def normalize_vortex(tokens, letter_type="generic"):
    out = []
    i = 0
    def mid_ok(tok):
        return tok.startswith("D") or tok in ("SEG_K","SEG_Q")
    while i < len(tokens):
        if tokens[i] in ("TURN+Q1","TURN-Q1"):
            t = tokens[i]
            sign = t[4]  # +/-
            j = i + 1
            while j < len(tokens) and mid_ok(tokens[j]): j += 1
            if j < len(tokens) and tokens[j] == f"TURN{sign}Q1":
                j2 = j + 1
                while j2 < len(tokens) and mid_ok(tokens[j2]): j2 += 1
                if j2 < len(tokens) and tokens[j2] == f"TURN{sign}Q1":
                    if letter_type == "ج":
                        out.append("JIM_VORTEX(Q3)")
                    else:
                        out.append("VORTEX(Q3)") # Generic vortex name
                    i = j2 + 1
                    continue
        out.append(tokens[i])
        i += 1
    return out

def rot4(x, d): return (x + d) & 3

def cube_update(tokens):
    c = [0]*18
    for t in tokens:
        if t.startswith("D"):
            k = int(t[1])
            ax = DIR_AXIS[k]
            c[ax] = rot4(c[ax], 1)
        elif t.startswith("TURN+Q1") or t.startswith("TURN-Q1"):
            c[0] = rot4(c[0], 1)
        elif t == "SEG_K":
            c[15] = rot4(c[15], 1)
        elif t == "SEG_Q":
            c[16] = rot4(c[16], 1)
        elif t == "LOOP":
            c[11] = rot4(c[11], 1)
        elif t == "JUNC":
            c[5] = rot4(c[5], 1)
        elif t == "NT":
            c[1] = rot4(c[1], 1)
        elif t == "NF":
            c[2] = rot4(c[2], 1)
        elif t == "NM":
            c[3] = rot4(c[3], 1)
        elif t == "JIM_VORTEX(Q3)" or t == "VORTEX(Q3)":
            c[0] = rot4(c[0], 3)
            c[9] = rot4(c[9], 1)
        else:
            # Skip unknown tokens like SEG_Q if not handled
            pass
    return c

def tag36_hex(c):
    v = 0
    for i in range(18):
        v |= (c[i] & 3) << (2*i)
    return f"{v:09x}"

def rle(tokens):
    out = []
    if not tokens: return out
    cur = tokens[0]; n = 1
    for t in tokens[1:]:
        if t == cur: n += 1
        else:
            out.append([cur, n])
            cur, n = t, 1
    out.append([cur, n])
    return out

def binarize_inv(gray):
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return (bw > 0).astype(np.uint8)

def remove_long_hlines(fg):
    H, W = fg.shape
    num, lbl, stats, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    keep = np.zeros_like(fg)
    for i in range(1, num):
        x,y,w,h,area = stats[i]
        if w >= int(0.90*W) and h <= 6:
            continue
        keep[lbl == i] = 1
    return keep

def split_body_nuq(fg):
    num, lbl, stats, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    if num <= 1:
        raise RuntimeError("no foreground")
    areas = stats[1:, cv2.CC_STAT_AREA]
    body_i = 1 + int(np.argmax(areas))
    body = (lbl == body_i).astype(np.uint8)
    nuq = np.zeros_like(fg)
    for i in range(1, num):
        if i == body_i: continue
        x,y,w,h,area = stats[i]
        if area <= 0.05 * stats[body_i, cv2.CC_STAT_AREA]:
            nuq[lbl == i] = 1
    return body, nuq

def bbox(mask):
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        raise RuntimeError("empty mask")
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())

def nuq_zone(nuq_mask, body_bbox):
    x0,y0,x1,y1 = body_bbox
    cy = (y0 + y1) / 2.0
    ys, xs = np.where(nuq_mask > 0)
    if len(xs) == 0:
        return []
    ny = ys.mean()
    if ny > y1:   return ["NT"]
    if ny < y0:   return ["NF"]
    if ny < cy - (y1-y0)/6: return ["NF"]
    if ny > cy + (y1-y0)/6: return ["NT"]
    return ["NM"]

def skel_graph(body):
    sk = skeletonize(body.astype(bool)).astype(np.uint8)
    ys, xs = np.where(sk > 0)
    pts = set(zip(xs, ys))
    G = nx.Graph()
    for (x,y) in pts:
        G.add_node((x,y))
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if dx==0 and dy==0: continue
                q = (x+dx, y+dy)
                if q in pts:
                    G.add_edge((x,y), q)
    return sk, G

def endpoints(G):
    return [n for n in G.nodes if G.degree[n] == 1]

def mainpath(G):
    eps = sorted(endpoints(G), key=lambda p:(p[0],p[1]))
    if len(eps) < 2:
        nodes = sorted(G.nodes, key=lambda p:(p[0],p[1]))
        eps = nodes[:2]
    start = eps[0]
    best_path = None
    best_len = -1
    for end in eps[1:]:
        try:
            p = nx.shortest_path(G, start, end)
        except nx.NetworkXNoPath:
            continue
        if len(p) > best_len:
            best_len = len(p)
            best_path = p
    if best_path is None:
        best_path = nx.shortest_path(G, eps[0], eps[-1])
    return best_path

def trace_from_path(path):
    tokens = []
    dirs = []
    tokens.append("SEG_Q")
    acc = 0
    for (x1,y1),(x2,y2) in zip(path, path[1:]):
        dx = int(np.sign(x2-x1))
        dy = int(np.sign(y2-y1))
        if (dx,dy) == (0,0): 
            continue
        d_tok, d_idx = DIR_MAP[(dx,dy)]
        tokens.append(d_tok)
        if dirs:
            prev = dirs[-1]
            d = signed_delta(prev, d_idx)
            acc += d
            while abs(acc) >= 2:
                sgn = "+" if acc > 0 else "-"
                tokens.append(f"TURN{sgn}Q1")
                acc -= 2 if acc > 0 else -2
        dirs.append(d_idx)
    return tokens

def run_extraction(img_path, letter_char):
    gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise RuntimeError(f"cannot read image: {img_path}")
    fg = binarize_inv(gray)
    fg = remove_long_hlines(fg)
    body, nuq = split_body_nuq(fg)
    x0,y0,x1,y1 = bbox(body)
    body_c = body[y0:y1+1, x0:x1+1]
    nuq_c = nuq[y0:y1+1, x0:x1+1]
    sk, G = skel_graph(body_c)
    path = mainpath(G)
    tokens = trace_from_path(path)
    tokens = normalize_vortex(tokens, letter_char)
    tokens.extend(nuq_zone(nuq_c, (0,0, body_c.shape[1]-1, body_c.shape[0]-1)))
    vortex_count = sum(1 for t in tokens if "VORTEX" in t)
    c = cube_update(tokens)
    tag = tag36_hex(c)
    return tokens, vortex_count, c, tag

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True)
    ap.add_argument("--char", default="generic")
    ap.add_argument("--rle", action="store_true")
    args = ap.parse_args()
    tokens, vc, c, tag = run_extraction(args.img, args.char)
    out = {
        "letter": args.char,
        "vortex_count": vc,
        "tag36_hex": tag,
        "cube_state": c,
        "trace": rle(tokens) if args.rle else tokens
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
