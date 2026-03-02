# Validation & Conformance Testing
Location: `scripts/validation/`

Contains runners for validating that the implementation conforms to the normative specification.

## Key Scripts
- `validate_st28.py`: Deep conformance validator for ST-28 datasets.
- `run_hl18_tests.py` / `run_hl18_ext.py`: Test suite runners for HijaiyyahLang core.
- `verify_hl18_release.py`: Local release integrity verifier for HL-18.
- `check_v18_duplicates.py` / `verify_and_build_v18.py`: Ensures uniqueness and injectivity of v18 features.
- `verify_vortex.py`: Geometric vortex property verification.
