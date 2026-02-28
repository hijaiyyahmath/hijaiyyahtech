#!/usr/bin/env bash
set -euo pipefail

WORK=/work
A_FILE="$WORK/A"
RESULTS="$WORK/results"
NORMDIR="$WORK/normaliz"

mkdir -p "$RESULTS" "$NORMDIR"
chmod 777 "$NORMDIR"
rm -f "$NORMDIR/generators.txt"

echo "=== Hijaiyah toolchain run ===" | tee "$RESULTS/manifest.txt"
date -u +"UTC %Y-%m-%d %H:%M:%S" | tee -a "$RESULTS/manifest.txt"
echo "PWD=$(pwd)" | tee -a "$RESULTS/manifest.txt"

# Check input exists
if [ ! -f "$A_FILE" ]; then
  echo "ERROR: matrix file /work/A not found." | tee -a "$RESULTS/manifest.txt"
  exit 1
fi

# Hash input (certificate)
echo "" | tee -a "$RESULTS/manifest.txt"
echo "== SHA256(A) ==" | tee -a "$RESULTS/manifest.txt"
sha256sum "$A_FILE" | tee -a "$RESULTS/manifest.txt"

# Versions (certificate)
echo "" | tee -a "$RESULTS/manifest.txt"
echo "== Tool versions ==" | tee -a "$RESULTS/manifest.txt"
echo "python: $(python --version 2>&1)" | tee -a "$RESULTS/manifest.txt"

# 4ti2 version output isn't always consistent; store help header as certificate
echo "" | tee -a "$RESULTS/manifest.txt"
echo "4ti2(markov) header:" | tee -a "$RESULTS/manifest.txt"
(markov 2>&1 | head -n 20) | tee -a "$RESULTS/manifest.txt" || true

echo "" | tee -a "$RESULTS/manifest.txt"
echo "normaliz header:" | tee -a "$RESULTS/manifest.txt"
(normaliz 2>&1 | head -n 40) | tee -a "$RESULTS/manifest.txt" || true

# ---- 4ti2: Markov basis & Groebner (toric ideal generators) ----
echo "" | tee -a "$RESULTS/manifest.txt"
echo "== Running 4ti2 ==" | tee -a "$RESULTS/manifest.txt"

# Run in /work so 4ti2 writes outputs next to input
cd "$WORK"

# 4ti2 expects A.mat and command uses basename A
cp -f /work/A /work/A.mat

echo "Command: markov -parb A" | tee -a "$RESULTS/manifest.txt"
markov -parb A | tee "$RESULTS/markov.log" || true

echo "Command: groebner -parb A" | tee -a "$RESULTS/manifest.txt"
groebner -parb A | tee "$RESULTS/groebner.log" || true

# Copy any A.* artifacts produced by 4ti2 as raw certificates
cp -f A.* "$RESULTS/" 2>/dev/null || true

# ---- Normaliz: generators + monoid normalization / Hilbert basis ----
echo "" | tee -a "$RESULTS/manifest.txt"
echo "== Running Normaliz ==" | tee -a "$RESULTS/manifest.txt"

python3 /usr/local/bin/make_normaliz_input.py /work/A /work/normaliz/generators.txt

IN=/work/normaliz/hijaiyah.in
: > "$IN"
printf "amb_space 14\n" >> "$IN"
printf "monoid 28\n"   >> "$IN"
cat /work/normaliz/generators.txt >> "$IN"
printf "normalization\n" >> "$IN"
printf "hilbert_basis\n"  >> "$IN"

echo "Normaliz input: $IN" | tee -a "$RESULTS/manifest.txt"
echo "Command: normaliz $IN" | tee -a "$RESULTS/manifest.txt"
normaliz "$IN" | tee "$RESULTS/normaliz.log" || true

# Copy Normaliz outputs (raw certificates)
cp -f "$NORMDIR"/hijaiyah.* "$RESULTS/" 2>/dev/null || true
cp -f "$NORMDIR"/*.txt "$RESULTS/" 2>/dev/null || true

echo "" | tee -a "$RESULTS/manifest.txt"
echo "== Done. Outputs in /work/results ==" | tee -a "$RESULTS/manifest.txt"
ls -la "$RESULTS" | tee -a "$RESULTS/manifest.txt"