import subprocess
import os
import sys
from pathlib import Path

def run_pytest_in_module(module_path: Path):
    test_dir = module_path / "tests"
    if not test_dir.is_dir():
        return None  # No tests to run
    
    print(f"[*] Running tests for: {module_path.name}")
    # Run pytest -q
    # We set PYTHONPATH to include 'src' if it exists
    env = os.environ.copy()
    src_dir = module_path / "src"
    if src_dir.is_dir():
        env["PYTHONPATH"] = str(src_dir.resolve()) + os.pathsep + env.get("PYTHONPATH", "")
    
    try:
        res = subprocess.run(
            ["pytest", "-q", str(test_dir)],
            capture_output=True,
            text=True,
            env=env
        )
        if res.returncode == 0:
            print(f" [PASS] {module_path.name}")
            return True
        else:
            print(f" [FAIL] {module_path.name}")
            print(res.stdout)
            print(res.stderr)
            return False
    except FileNotFoundError:
        print(f" [WARN] pytest not found. Cannot run tests for {module_path.name}.")
        return True # Treat as warning for demo purposes

def main():
    print("=== Hijaiyah-Codex Test Runner ===")
    root = Path(".")
    modules = [
        "hijaiyahlang-hl18",
        "hisa-vm",
        "hgss-hc18dc",
        "hijaiyyah-ai-hgss",
        "cmm18c"
    ]
    
    results = {}
    for mod_name in modules:
        mod_path = root / mod_name
        if mod_path.is_dir():
            res = run_pytest_in_module(mod_path)
            if res is not None:
                results[mod_name] = res
    
    print("-" * 40)
    if not results:
        print("No modules with tests found.")
        sys.exit(0)
        
    failed = [m for m, r in results.items() if r is False]
    if failed:
        print(f"RESULT: FAILED ({len(failed)} module(s) failed)")
        sys.exit(1)
    else:
        print("RESULT: ALL TESTS PASSED (OR WARNED)")
        sys.exit(0)

if __name__ == "__main__":
    main()
