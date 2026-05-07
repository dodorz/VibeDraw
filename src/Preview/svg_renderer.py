from __future__ import annotations

from html import escape
from typing import Any


PADDING = 16
LAYER_STYLES = {
    "BRIDGE_GIRDER": {"stroke": "#1f2937", "fill": "none"},
    "BRIDGE_DECK": {"stroke": "#0f766e", "fill": "rgba(15, 118, 110, 0.12)"},
    "BRIDGE_SECTION": {"stroke": "#b45309", "fill": "rgba(180, 83, 9, 0.10)"},
    "DIM": {"stroke": "#475569", "fill": "none"},
    "TEXT": {"stroke": "none", "fill": "#111827"},
}


def render_svg_document(instruction_batch: dict[str, Any]) -> str:
    bounds = _compute_bounds(instruction_batch["instructions"])
    min_x, min_y, max_x, max_y = bounds
    width = max(int(max_x - min_x + (PADDING * 2)), 1)
    height = max(int(max_y - min_y + (PADDING * 2)), 1)

    body = []
    for instruction in instruction_batch["instructions"]:
        body.extend(_render_instruction(instruction, bounds))

    svg_body = "\n  ".join(body)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="VibeDraw preview">\n'
        f'  <rect width="{width}" height="{height}" fill="#f8fafc" />\n'
        f'  {svg_body}\n'
        f"</svg>\n"
    )


def _compute_bounds(instructions: list[dict[str, Any]]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []

    for instruction in instructions:
        for point in _instruction_points(instruction):
            xs.append(float(point[0]))
            ys.append(float(point[1]))

    if not xs or not ys:
        return (0.0, 0.0, 1.0, 1.0)

    return (min(xs), min(ys), max(xs), max(ys))


def _instruction_points(instruction: dict[str, Any]) -> list[list[float]]:
    kind = instruction["kind"]
    if kind == "polyline":
        return instruction["points"]
    if kind == "line":
        return [instruction["from"], instruction["to"]]
    if kind == "text":
        return [instruction["position"]]
    if kind == "aligned_dimension":
        return [
            instruction["from"],
            instruction["to"],
            instruction["dimension_line_point"],
        ]
    return []


def _map_point(point: list[float], bounds: tuple[float, float, float, float]) -> tuple[float, float]:
    min_x, min_y, _max_x, max_y = bounds
    x = float(point[0]) - min_x + PADDING
    y = max_y - float(point[1]) + PADDING
    return (x, y)


def _style_for_layer(layer: str) -> dict[str, str]:
    return LAYER_STYLES.get(layer, {"stroke": "#334155", "fill": "none"})


def _render_instruction(
    instruction: dict[str, Any],
    bounds: tuple[float, float, float, float],
) -> list[str]:
    kind = instruction["kind"]
    if kind == "polyline":
        return [_render_polyline(instruction, bounds)]
    if kind == "line":
        return [_render_line(instruction, bounds)]
    if kind == "text":
        return [_render_text(instruction, bounds)]
    if kind == "aligned_dimension":
        return _render_aligned_dimension(instruction, bounds)
    raise ValueError(f"Unsupported instruction kind: {kind}")


def _render_polyline(
    instruction: dict[str, Any],
    bounds: tuple[float, float, float, float],
) -> str:
    style = _style_for_layer(instruction["layer"])
    points = [_map_point(point, bounds) for point in instruction["points"]]
    points_attr = " ".join(f"{x},{y}" for x, y in points)
    fill = style["fill"] if instruction["closed"] else "none"
    return (
        f'<polyline points="{points_attr}" stroke="{style["stroke"]}" '
        f'fill="{fill}" stroke-width="1.5" />'
    )


def _render_line(
    instruction: dict[str, Any],
    bounds: tuple[float, float, float, float],
) -> str:
    style = _style_for_layer(instruction["layer"])
    start_x, start_y = _map_point(instruction["from"], bounds)
    end_x, end_y = _map_point(instruction["to"], bounds)
    return (
        f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" '
        f'stroke="{style["stroke"]}" stroke-width="1.5" />'
    )


def _render_text(
    instruction: dict[str, Any],
    bounds: tuple[float, float, float, float],
) -> str:
    style = _style_for_layer(instruction["layer"])
    x, y = _map_point(instruction["position"], bounds)
    baseline_y = y - 4
    text = escape(instruction["text"])
    height = instruction["height"] * 3
    return (
        f'<text x="{x}" y="{baseline_y}" fill="{style["fill"]}" '
        f'font-family="Consolas, monospace" font-size="{height}">{text}</text>'
    )


def _render_aligned_dimension(
    instruction: dict[str, Any],
    bounds: tuple[float, float, float, float],
) -> list[str]:
    style = _style_for_layer(instruction["layer"])
    from_x, from_y = _map_point(instruction["from"], bounds)
    to_x, to_y = _map_point(instruction["to"], bounds)
    dim_x, dim_y = _map_point(instruction["dimension_line_point"], bounds)
    text = escape(instruction["text"])

    return [
        (
            f'<line x1="{from_x}" y1="{from_y}" x2="{to_x}" y2="{to_y}" '
            f'stroke="{style["stroke"]}" stroke-width="1" stroke-dasharray="4 2" />'
        ),
        (
            f'<text x="{dim_x}" y="{dim_y - 4}" fill="{style["stroke"]}" '
            f'font-family="Consolas, monospace" font-size="10" text-anchor="middle">{text}</text>'
        ),
    ]

