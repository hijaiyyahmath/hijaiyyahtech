from __future__ import annotations
import argparse
import json

from hisavm.master import load_master_csv
from hisavm.bytecode import load_bin
from hisavm.vm import HisaVM, Trap
from hisavm.constants import MASTER_CSV_PATH_DEFAULT, HIJAIYYAH_28_PATH_DEFAULT

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--program", required=True)
    ap.add_argument("--master", default=MASTER_CSV_PATH_DEFAULT)
    ap.add_argument("--hij28", default=HIJAIYYAH_28_PATH_DEFAULT)
    ap.add_argument("--trace", default=None)
    args = ap.parse_args()

    # ensure paths are absolute or relative to hisa-vm root
    # for simplicity, we assume we run from hisa-vm root
    v18_by_index, rows = load_master_csv(args.master, args.hij28, strict_formulas=True)
    code = load_bin(args.program)

    vm = HisaVM(code=code, v18_by_index=v18_by_index)
    
    try:
        steps = vm.run()
        status = {"state": "HALT", "err": vm.st.ERR, "steps": steps}
    except Trap as t:
        status = {"state": "TRAP", "err": t.err, "steps": 0, "msg": str(t)}

    out = {
        "status": status,
        "CLOSED_HINT": vm.st.CLOSED_HINT,
    }
    s = json.dumps(out, ensure_ascii=False, indent=2)
    print(s)

    if args.trace:
        import os
        os.makedirs(os.path.dirname(args.trace) or ".", exist_ok=True)
        open(args.trace, "w", encoding="utf-8").write(s + "\n")

if __name__ == "__main__":
    main()
