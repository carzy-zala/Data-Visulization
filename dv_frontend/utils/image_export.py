# utils/image_export.py
from __future__ import annotations
from typing import Optional

def altair_to_png(
    chart,
    *,
    scale: float = 2.0,
    width: Optional[int] = None,
    height: Optional[int] = None,
    background: Optional[str] = "white"  # Optional: "white" or "transparent"
) -> bytes:
    """
    Export an Altair chart to PNG using vl-convert-python directly.
    Dependencies: pip install vl-convert-python
    """
    if chart is None:
        raise ValueError("No chart object provided.")

    try:
        import vl_convert as vlc
    except Exception as e:
        raise RuntimeError(
            "vl-convert-python is not installed. Run: pip install vl-convert-python"
        ) from e

    # Convert chart to Vega-Lite spec dict
    spec = chart.to_dict()

    # Inject optional size & background
    if width is not None:
        spec["width"] = int(width)
    if height is not None:
        spec["height"] = int(height)
    if background is not None:
        spec["background"] = background  # "white" or "transparent"

    try:
        # Convert Vega-Lite to PNG bytes
        return vlc.vegalite_to_png(spec, scale=scale)
    except Exception as e:
        raise RuntimeError("PNG export via vl-convert failed.") from e
