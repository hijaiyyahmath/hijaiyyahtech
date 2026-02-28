# Glyph Raster Assets

This directory contains rasterized images (`.png`) of Hijaiyah characters and debug artifacts.

## 1. Contents
- **Character Glyphs**: Raster versions of Hijaiyah letters (e.g., `ء.png`, `ه.png`).
- **Audit Debugging**: Visual output from OCR and skeletonization tests (e.g., `_debug_jeem_skel.png`).
- **Legacy/Temp**: Temporary processed images used during feature development.

## 2. Usage
These images are used as inputs for:
- OCR validation in `hijaiyahlang-hl18`.
- Visual forensic audit in `hijaiyyah-ai-hgss`.
- Debugging the skeletonization pipeline for geometry extraction.

## 3. Governance
Raster assets should be synchronized with the normative SVG assets in the parent `glyph/` directory. Any new rasterized output from tools should be placed here or in `artifacts/` if it is run-specific.
