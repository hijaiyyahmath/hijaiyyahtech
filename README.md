# HijaiyyahMath.org

**Matematika Hijaiyyah Technology Stack v1.0**

A deterministic, audit-aware technology stack built from Hijaiyyah geometric codex (v18), spanning language, ISA, compute (silicon/photonic/qubit), AI harness, and optional security module (HGSS/HC18DC).

## 🌐 Live Website

**[https://hijaiyyahmath.github.io/hijaiyyahtech/](https://hijaiyyahmath.github.io/hijaiyyahtech/)**

## Stack Components

| Component | Description |
|-----------|-------------|
| **HL-18** | HijaiyyahLang — Word-to-Vector (v18) audit engine |
| **H-ISA** | Hijaiyyah ISA — Audit-centric instruction set via HISA-VM |
| **HCPU** | Deterministic compute module (Silicon/Photonic/Qubit) |
| **CMM18C** | Certified Mathematical Machine 18-dimensional compiler |

## Auditor Bundle

Download the offline auditor bundle from the [Releases](https://github.com/hijaiyyahmath/hijaiyyahtech/releases) page.

```bash
# Linux/macOS
./scripts/audit.sh

# Windows
powershell -ExecutionPolicy Bypass -File .\scripts\audit.ps1
```

## Development

```bash
cd web/apps/hijaiyyahmath-org
npm install
npm run dev
```

## Deployment

This site is automatically deployed to GitHub Pages on every push to `master` via GitHub Actions.

## License

© 2026 Hijaiyyah Tech
