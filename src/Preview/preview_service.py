from __future__ import annotations

from pathlib import Path

from src.CadInstructions import create_cad_instruction_batch
from src.DrawingPlanner import create_drawing_plan, load_bridge_model_fixture
from src.Preview.svg_renderer import render_svg_document


def build_preview_svg(bridge_model_path: str | Path) -> str:
    bridge_model = load_bridge_model_fixture(bridge_model_path)
    return render_preview_from_bridge_model(bridge_model)


def render_preview_from_bridge_model(bridge_model: dict) -> str:
    drawing_plan = create_drawing_plan(bridge_model)
    batch = create_cad_instruction_batch(bridge_model, drawing_plan)
    return render_svg_document(batch)

