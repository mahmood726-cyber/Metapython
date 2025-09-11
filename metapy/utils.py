from __future__ import annotations
from typing import Optional

def fmt_num(x: Optional[float], fmt: str = "{:.3f}") -> str:
    if x is None:
        return "N/A"
    try:
        return fmt.format(float(x))
    except Exception:
        return str(x)