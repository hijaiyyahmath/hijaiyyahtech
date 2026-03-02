import subprocess
import sys
import os
from pathlib import Path

def run_script(script_name):
    print(f"\n>>> Executing {script_name}...")
    try:
        res = subprocess.run([sys.executable, f"scripts/{script_name}"], text=True)
        return res.returncode == 0
    except Exception as e:
        print(f"Execution Error: {e}")
        return False

def main():
    print("==========================================")
    print("   HIJAIYYAH-CODEX FULL PIPELINE RUNNER    ")
    print("==========================================")
    
    pipeline = [
        "env_check.py",
        "run_tests_all.py",
        "run_demos_all.py"
    ]
    
    for script in pipeline:
        if not run_script(script):
            print(f"\n[FATAL] Pipeline stopped at {script}")
            sys.exit(1)
            
    print("\n==========================================")
    print("   SUCCESS: ALL SYSTEMS NOMINAL           ")
    print("==========================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
