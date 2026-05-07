from typing import Any


def _normalize_number(value: float) -> int | float:
    integer_value = int(value)
    if integer_value == value:
        return integer_value
    return value


def _cumulative_span_points(spans_m: list[float]) -> list[float]:
    points = [0.0]
    running_total = 0.0
    for span in spans_m:
        running_total += span
        points.append(running_total)
    return points


def _view_map(drawing_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {view["view_id"]: view for view in drawing_plan["views"]}


def _elevation_instructions(
    bridge_model: dict[str, Any],
    elevation_view: dict[str, Any],
) -> list[dict[str, Any]]:
    spans_m = bridge_model["bridge"]["spans_m"]
    span_points = _cumulative_span_points(spans_m)
    origin_x, origin_y = elevation_view["origin"]

    instructions = [
        {
            "kind": "polyline",
            "id": "elevation_girder_bottom",
            "layer": "BRIDGE_GIRDER",
            "view_id": elevation_view["view_id"],
            "source_component_id": "main_girder",
            "points": [
                [_normalize_number(origin_x + x), _normalize_number(origin_y)]
                for x in span_points
            ],
            "closed": False,
        }
    ]

    for index, span in enumerate(spans_m, start=1):
        start_x = origin_x + span_points[index - 1]
        end_x = origin_x + span_points[index]
        instructions.append(
            {
                "kind": "aligned_dimension",
                "id": f"dim_span_{index}",
                "layer": "DIM",
                "view_id": elevation_view["view_id"],
                "source_component_id": f"span_{index}",
                "from": [
                    _normalize_number(start_x),
                    _normalize_number(origin_y - 5),
                ],
                "to": [
                    _normalize_number(end_x),
                    _normalize_number(origin_y - 5),
                ],
                "dimension_line_point": [
                    _normalize_number((start_x + end_x) / 2),
                    _normalize_number(origin_y - 12),
                ],
                "text": f"{_format_length(span)}m",
            }
        )

    return instructions


def _plan_instructions(
    bridge_model: dict[str, Any],
    plan_view: dict[str, Any],
) -> list[dict[str, Any]]:
    deck_width_m = bridge_model["bridge"]["deck_width_m"]
    total_length = sum(bridge_model["bridge"]["spans_m"])
    origin_x, origin_y = plan_view["origin"]
    half_width = deck_width_m / 2

    return [
        {
            "kind": "polyline",
            "id": "plan_deck_outline",
            "layer": "BRIDGE_DECK",
            "view_id": plan_view["view_id"],
            "source_component_id": "deck_outline",
            "points": [
                [origin_x, origin_y - half_width],
                [origin_x + total_length, origin_y - half_width],
                [origin_x + total_length, origin_y + half_width],
                [origin_x, origin_y + half_width],
            ],
            "closed": True,
        }
    ]


def _typical_section_instructions(
    bridge_model: dict[str, Any],
    section_view: dict[str, Any],
) -> list[dict[str, Any]]:
    deck_width_m = bridge_model["bridge"]["deck_width_m"]
    origin_x, origin_y = section_view["origin"]
    depth_m = _resolve_section_depth(bridge_model)

    return [
        {
            "kind": "polyline",
            "id": "typical_section_outline",
            "layer": "BRIDGE_SECTION",
            "view_id": section_view["view_id"],
            "source_component_id": "typical_section",
            "points": [
                [origin_x, origin_y],
                [origin_x + deck_width_m, origin_y],
                [origin_x + deck_width_m, origin_y - depth_m],
                [origin_x, origin_y - depth_m],
            ],
            "closed": True,
        }
    ]


def _resolve_section_depth(bridge_model: dict[str, Any]) -> float:
    superstructure = bridge_model["bridge"]["superstructure"]
    if superstructure["girder_depth_policy"] == "manual":
        return float(superstructure["girder_depth_m"])
    return 2.5


def _format_length(length_m: float) -> str:
    integer_value = int(length_m)
    if integer_value == length_m:
        return str(integer_value)
    return str(length_m)


def create_cad_instruction_batch(
    bridge_model: dict[str, Any],
    drawing_plan: dict[str, Any],
) -> dict[str, Any]:
    views = _view_map(drawing_plan)
    instructions = []
    instructions.extend(_elevation_instructions(bridge_model, views["elevation_main"]))
    instructions.extend(_plan_instructions(bridge_model, views["plan_main"]))
    instructions.extend(
        _typical_section_instructions(bridge_model, views["typical_section_main"])
    )
    instructions.append(
        {
            "kind": "text",
            "id": "title_general_arrangement",
            "layer": "TEXT",
            "view_id": views["elevation_main"]["view_id"],
            "source_component_id": "drawing_title",
            "position": [0, 10],
            "text": "GENERAL ARRANGEMENT",
            "height": 3.5,
        }
    )

    return {
        "project_id": drawing_plan["project_id"],
        "drawing_id": drawing_plan["drawing_id"],
        "instructions": instructions,
    }
