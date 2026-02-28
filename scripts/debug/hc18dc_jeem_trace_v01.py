import cv2
import numpy as np
import networkx as nx
from skimage.morphology import skeletonize

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

# vortex_norm fixed: 3xTURN±Q1 -> JIM_VORTEX(Q3)
def normalize_vortex(tokens):
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
                    out.append("JIM_VORTEX(Q3)")
                    i = j2 + 1
                    continue
        out.append(tokens[i])
        i += 1
    return out

# Cube state: 18 rotors mod4
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
        elif t == "JIM_VORTEX(Q3)":
            # FIXED PRIMITIVE (WAJIB): axis0 +3, axis9 +1
            c[0] = rot4(c[0], 3)
            c[9] = rot4(c[9], 1)
        else:
            raise ValueError(f"Unknown token: {t}")
    return c

def tag36_hex(c):
    # pack 2 bits per axis into 36-bit integer (little packing order)
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

# ---------------- Preprocess: remove guide lines & split body/nuq ----------------
def binarize_inv(gray):
    # black strokes -> 1
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return (bw > 0).astype(np.uint8)

def remove_long_hlines(fg):
    H, W = fg.shape
    num, lbl, stats, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    keep = np.zeros_like(fg)
    for i in range(1, num):
        x,y,w,h,area = stats[i]
        # remove line-like components spanning most width, thin height
        if w >= int(0.90*W) and h <= 6:
            continue
        keep[lbl == i] = 1
    return keep

def split_body_nuq(fg):
    num, lbl, stats, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    if num <= 1:
        raise RuntimeError("no foreground")
    # largest component as body
    areas = stats[1:, cv2.CC_STAT_AREA]
    body_i = 1 + int(np.argmax(areas))
    body = (lbl == body_i).astype(np.uint8)

    # nuq candidates: other small components
    nuq = np.zeros_like(fg)
    for i in range(1, num):
        if i == body_i: continue
        x,y,w,h,area = stats[i]
        # heuristik: nuq kecil
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
    # classify each component by its centroid y relative to body bbox
    # simple: overall centroid
    ny = ys.mean()
    if ny > y1:   return ["NT"]   # below
    if ny < y0:   return ["NF"]   # above
    # middle: split by thirds
    if ny < cy - (y1-y0)/6: return ["NF"]
    if ny > cy + (y1-y0)/6: return ["NT"]
    return ["NM"]

# ---------------- Skeleton graph + MainPath ----------------
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
        # fallback
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

# ---------------- Trace extraction with 45° accumulator -> Q1 ----------------
def trace_from_path(path):
    tokens = []
    dirs = []

    # segment label: jeem is curved => SEG_Q (rule: any turn => SEG_Q)
    tokens.append("SEG_Q")

    acc = 0  # accumulator in 45° units
    for (x1,y1),(x2,y2) in zip(path, path[1:]):
        dx = int(np.sign(x2-x1))
        dy = int(np.sign(y2-y1))
        if (dx,dy) == (0,0): 
            continue
        d_tok, d_idx = DIR_MAP[(dx,dy)]
        tokens.append(d_tok)

        if dirs:
            prev = dirs[-1]
            d = signed_delta(prev, d_idx)   # 45° units
            acc += d
            # emit Q1 per 90° accumulated
            while abs(acc) >= 2:
                sgn = "+" if acc > 0 else "-"
                tokens.append(f"TURN{sgn}Q1")
                acc -= 2 if acc > 0 else -2
        dirs.append(d_idx)

    return tokens

def run(img_path):
    gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise RuntimeError("cannot read image")

    fg = binarize_inv(gray)
    fg = remove_long_hlines(fg)
    body, nuq = split_body_nuq(fg)

    # crop to body bbox for stability
    x0,y0,x1,y1 = bbox(body)
    body_c = body[y0:y1+1, x0:x1+1]
    nuq_c = nuq[y0:y1+1, x0:x1+1]

    sk, G = skel_graph(body_c)
    path = mainpath(G)

    tokens = trace_from_path(path)
    tokens = normalize_vortex(tokens)

    # append nuq tokens at end so they don't break vortex normalization
    tokens.extend(nuq_zone(nuq_c, (0,0, body_c.shape[1]-1, body_c.shape[0]-1)))

    # checks
    vortex_count = sum(1 for t in tokens if t == "JIM_VORTEX(Q3)")
    c = cube_update(tokens)
    tag = tag36_hex(c)

    return tokens, vortex_count, c, tag

if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True)
    ap.add_argument("--rle", action="store_true")
    args = ap.parse_args()

    tokens, vc, c, tag = run(args.img)

    out = {
        "letter": "ج",
        "vortex_count": vc,
        "tag36_hex": tag,
        "cube_state": c,
        "trace": rle(tokens) if args.rle else tokens
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print("JIM_VORTEX(Q3) count =", vc)
