import json
from pathlib import Path
from typing import Any


DEFAULT_DRAWING_ID = "general_arrangement_001"
DEFAULT_SHEET_SIZE = "A1"
DEFAULT_SHEET_SCALE = 200
VIEW_LAYOUTS = (
    {
        "view_id": "elevation_main",
        "type": "elevation",
        "origin": [0, 0],
        "scale": 200,
    },
    {
        "view_id": "plan_main",
        "type": "plan",
        "origin": [0, -120],
        "scale": 200,
    },
    {
        "view_id": "typical_section_main",
        "type": "typical_section",
        "origin": [190, 0],
        "scale": 100,
    },
)


def load_bridge_model_fixture(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def create_drawing_plan(bridge_model: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": bridge_model["project_id"],
        "drawing_id": DEFAULT_DRAWING_ID,
        "drawing_type": "general_arrangement",
        "sheet": {
            "size": DEFAULT_SHEET_SIZE,
            "scale": DEFAULT_SHEET_SCALE,
        },
        "views": [dict(view) for view in VIEW_LAYOUTS],
    }
