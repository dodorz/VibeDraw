from __future__ import annotations

import re
from typing import Any


DEFAULT_DRAWINGS = [
    "general_arrangement",
    "plan",
    "elevation",
    "typical_section",
]
DRAWING_VIEW_TYPES = {"plan", "elevation", "typical_section"}


def parse_prompt_to_intent(prompt: str) -> dict[str, Any]:
    text = normalize_prompt(prompt)
    assumptions: list[str] = []

    spans = extract_spans(text)
    if not spans:
        spans = [40.0, 70.0, 40.0]
        assumptions.append("Spans were not detected, so the canonical MVP spans were assumed.")

    deck_width = extract_deck_width(text)
    if deck_width is None:
        deck_width = 7.5
        assumptions.append("Deck width was not detected, so 7.5 m was assumed.")

    section_type = detect_section_type(text)
    if section_type is None:
        section_type = "single_box_single_cell"
        assumptions.append("Section type was not detected, so single-box single-cell was assumed.")

    pier_type = detect_pier_type(text)
    if pier_type is None:
        pier_type = "double_column"
        assumptions.append("Pier type was not detected, so double-column piers were assumed.")

    abutment_type = detect_abutment_type(text)
    if abutment_type is None:
        abutment_type = "gravity"
        assumptions.append("Abutment type was not detected, so gravity abutments were assumed.")

    start_station = extract_start_station(text) or "K0+000"
    if start_station == "K0+000" and "K0+000" not in text.upper():
        assumptions.append("Start station was not detected, so K0+000 was assumed.")

    girder_depth_m = extract_girder_depth(text)
    girder_depth_policy = "manual" if girder_depth_m is not None else "auto"
    if girder_depth_m is None:
        assumptions.append("Girder depth was not specified, so automatic girder depth was assumed.")

    requested_drawings = detect_requested_drawings(text)
    if requested_drawings is None:
        requested_drawings = list(DEFAULT_DRAWINGS)
        assumptions.append("Requested drawings were not detected, so plan, elevation, and typical section were assumed.")

    assumptions.insert(0, "Bridge type is assumed to be a prestressed continuous girder bridge.")

    superstructure: dict[str, Any] = {
        "section_type": section_type,
        "girder_depth_policy": girder_depth_policy,
    }
    if girder_depth_m is not None:
        superstructure["girder_depth_m"] = girder_depth_m

    return {
        "bridge_type": "continuous_girder",
        "material": "prestressed_concrete",
        "spans_m": spans,
        "deck_width_m": deck_width,
        "alignment_type": "straight",
        "start_station": start_station,
        "superstructure": superstructure,
        "substructure": {
            "pier_type": pier_type,
            "abutment_type": abutment_type,
        },
        "requested_drawings": requested_drawings,
        "assumptions": assumptions,
        "questions": [],
    }


def normalize_prompt(prompt: str) -> str:
    return (
        prompt.replace("＋", "+")
        .replace("，", ",")
        .replace("。", ".")
        .replace("米", "m")
        .replace("宽度", "宽")
    )


def extract_spans(text: str) -> list[float]:
    match = re.search(r"(\d+(?:\.\d+)?(?:\s*\+\s*\d+(?:\.\d+)?)+)\s*m?(?:跨径|span|spans?)", text, re.IGNORECASE)
    if not match:
        return []
    spans: list[float] = []
    for part in match.group(1).split("+"):
        value = float(part.strip())
        spans.append(int(value) if value.is_integer() else value)
    return spans


def extract_deck_width(text: str) -> float | None:
    match = re.search(r"(?:桥宽|deck width|width)\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*m", text, re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    return int(value) if value.is_integer() else value


def extract_start_station(text: str) -> str | None:
    match = re.search(r"K\d+\+\d+", text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def extract_girder_depth(text: str) -> float | None:
    match = re.search(r"(?:梁高|girder depth)\s*(\d+(?:\.\d+)?)\s*m", text, re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    return int(value) if value.is_integer() else value


def detect_section_type(text: str) -> str | None:
    if re.search(r"单箱双室|double cell", text, re.IGNORECASE):
        return "single_box_double_cell"
    if re.search(r"单箱单室|single cell", text, re.IGNORECASE):
        return "single_box_single_cell"
    return None


def detect_pier_type(text: str) -> str | None:
    if re.search(r"实体墩|solid pier", text, re.IGNORECASE):
        return "solid_pier"
    if re.search(r"双柱墩|double[- ]column", text, re.IGNORECASE):
        return "double_column"
    return None


def detect_abutment_type(text: str) -> str | None:
    if re.search(r"搭板|seat abutment|seat", text, re.IGNORECASE):
        return "seat"
    if re.search(r"重力式|gravity", text, re.IGNORECASE):
        return "gravity"
    return None


def detect_requested_drawings(text: str) -> list[str] | None:
    normalized = text.lower()
    include: set[str] = set()
    exclude: set[str] = set()

    if re.search(r"(只|仅|only).*(断面图|横断面|截面图|section)", normalized, re.IGNORECASE):
        return ["general_arrangement", "typical_section"]
    if re.search(r"(只|仅|only).*(平面图|plan)", normalized, re.IGNORECASE):
        return ["general_arrangement", "plan"]
    if re.search(r"(只|仅|only).*(立面图|elevation)", normalized, re.IGNORECASE):
        return ["general_arrangement", "elevation"]

    if _mentions_general_arrangement(normalized):
        include.add("general_arrangement")
    if _mentions_plan(normalized):
        include.add("plan")
    if _mentions_elevation(normalized):
        include.add("elevation")
    if _mentions_typical_section(normalized):
        include.add("typical_section")

    if re.search(r"(不要|不出|去掉|取消|remove|without|exclude|drop).*(平面图|plan)", normalized, re.IGNORECASE):
        exclude.add("plan")
    if re.search(r"(不要|不出|去掉|取消|remove|without|exclude|drop).*(立面图|elevation)", normalized, re.IGNORECASE):
        exclude.add("elevation")
    if re.search(r"(不要|不出|去掉|取消|remove|without|exclude|drop).*(断面图|横断面|截面图|section)", normalized, re.IGNORECASE):
        exclude.add("typical_section")

    if not include and not exclude:
        return None

    requested = set(DEFAULT_DRAWINGS if exclude else ["general_arrangement"])
    if include:
        requested.update(include)
    requested.difference_update(exclude)
    if DRAWING_VIEW_TYPES.isdisjoint(requested):
        requested.update(DRAWING_VIEW_TYPES)
    ordered = [drawing for drawing in DEFAULT_DRAWINGS if drawing in requested]
    return ordered or list(DEFAULT_DRAWINGS)


def _mentions_general_arrangement(text: str) -> bool:
    return bool(re.search(r"总图|general arrangement|ga drawing", text, re.IGNORECASE))


def _mentions_plan(text: str) -> bool:
    return bool(re.search(r"平面图|plan view|plan\b", text, re.IGNORECASE))


def _mentions_elevation(text: str) -> bool:
    return bool(re.search(r"立面图|elevation view|elevation\b", text, re.IGNORECASE))


def _mentions_typical_section(text: str) -> bool:
    return bool(re.search(r"断面图|横断面|截面图|typical section|section view|\bsection\b", text, re.IGNORECASE))


def create_patch_response(current_model: dict[str, Any], prompt: str) -> dict[str, Any]:
    text = normalize_prompt(prompt)
    patches: list[dict[str, Any]] = []
    affected_views: set[str] = set()

    spans = extract_spans(text)
    if spans and spans != current_model["bridge"]["spans_m"]:
        patches.append({"op": "replace", "path": "/bridge/spans_m", "value": spans})
        affected_views.update({"plan", "elevation", "typical_section"})
    else:
        middle_span_match = re.search(r"(?:middle span|中跨)(?:改成|to|=)?\s*(\d+(?:\.\d+)?)\s*m", text, re.IGNORECASE)
        if middle_span_match and len(current_model["bridge"]["spans_m"]) >= 3:
            middle = float(middle_span_match.group(1))
            middle = int(middle) if middle.is_integer() else middle
            patches.append({"op": "replace", "path": "/bridge/spans_m/1", "value": middle})
            affected_views.update({"plan", "elevation", "typical_section"})

    deck_width = extract_deck_width(text)
    if deck_width is not None and deck_width != current_model["bridge"]["deck_width_m"]:
        patches.append({"op": "replace", "path": "/bridge/deck_width_m", "value": deck_width})
        affected_views.update({"plan", "typical_section"})

    section_type = detect_section_type(text)
    if section_type and section_type != current_model["bridge"]["superstructure"]["section_type"]:
        patches.append(
            {
                "op": "replace",
                "path": "/bridge/superstructure/section_type",
                "value": section_type,
            }
        )
        affected_views.add("typical_section")

    pier_type = detect_pier_type(text)
    if pier_type and pier_type != current_model["bridge"]["substructure"]["pier_type"]:
        patches.append(
            {
                "op": "replace",
                "path": "/bridge/substructure/pier_type",
                "value": pier_type,
            }
        )
        affected_views.add("elevation")

    abutment_type = detect_abutment_type(text)
    if abutment_type and abutment_type != current_model["bridge"]["substructure"]["abutment_type"]:
        patches.append(
            {
                "op": "replace",
                "path": "/bridge/substructure/abutment_type",
                "value": abutment_type,
            }
        )
        affected_views.add("elevation")

    girder_depth = extract_girder_depth(text)
    if girder_depth is not None:
        patches.append(
            {
                "op": "replace",
                "path": "/bridge/superstructure/girder_depth_policy",
                "value": "manual",
            }
        )
        patches.append(
            {
                "op": "replace",
                "path": "/bridge/superstructure/girder_depth_m",
                "value": girder_depth,
            }
        )
        affected_views.update({"elevation", "typical_section"})

    requested_drawings = detect_requested_drawings(text)
    current_drawings = current_model["bridge"].get("drawings", list(DEFAULT_DRAWINGS))
    if requested_drawings and requested_drawings != current_drawings:
        patches.append(
            {
                "op": "replace",
                "path": "/bridge/drawings",
                "value": requested_drawings,
            }
        )
        affected_views.update(
            view
            for view in DRAWING_VIEW_TYPES
            if view in set(current_drawings) or view in set(requested_drawings)
        )

    return {
        "patches": patches,
        "affected_views": sorted(affected_views),
    }
