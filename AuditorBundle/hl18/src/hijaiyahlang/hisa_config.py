from __future__ import annotations
from pathlib import Path
import yaml
from .errors import ConformanceError
from .hisa_bridge import HisaIntegrationConfig

def load_hisa_integration_spec(path: str | Path) -> HisaIntegrationConfig:
    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    hisa = spec.get("hisa", {})
    try:
        return HisaIntegrationConfig(
            asm_cmd=tuple(hisa["asm_cmd"]),
            run_cmd=tuple(hisa["run_cmd"]),
            program_template=str(hisa["program_template"]),
            source_ext=str(hisa.get("source_ext", ".hisaasm")),
        )
    except Exception as e:
        raise ConformanceError(f"Invalid HISA integration spec: {e}") from e
