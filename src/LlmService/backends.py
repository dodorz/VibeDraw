from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from src.LlmService.parsing import create_patch_response, parse_prompt_to_intent


class MockIntentBackend:
    def parse_initial_intent(self, prompt: str) -> dict[str, Any]:
        intent = parse_prompt_to_intent(prompt)
        return {
            "intent": intent,
            "assumptions": intent["assumptions"],
            "questions": intent["questions"],
        }

    def patch_model(self, current_model: dict[str, Any], prompt: str) -> dict[str, Any]:
        return create_patch_response(current_model, prompt)


class OllamaIntentBackend:
    def __init__(self, base_url: str = "http://127.0.0.1:11434") -> None:
        self.base_url = base_url.rstrip("/")

    def parse_initial_intent(self, prompt: str, model: str) -> dict[str, Any]:
        system_prompt = (
            "You are an intent parser for a bridge engineering CAD tool. "
            "Return JSON only. Do not include markdown. "
            "The JSON must contain keys: intent, assumptions, questions. "
            "intent must contain bridge_type, material, spans_m, deck_width_m, "
            "alignment_type, start_station, superstructure, substructure, "
            "requested_drawings, assumptions, questions. "
            "Allowed values: bridge_type=continuous_girder; material=prestressed_concrete; "
            "superstructure.section_type=single_box_single_cell or single_box_double_cell; "
            "superstructure.girder_depth_policy=auto or manual; "
            "substructure.pier_type=double_column or solid_pier; "
            "substructure.abutment_type=gravity or seat; "
            "requested_drawings can include general_arrangement, plan, elevation, typical_section. "
            "If information is missing, make conservative bridge-engineering assumptions and list them."
        )
        response = self._generate_json(model, system_prompt, prompt)
        return _coerce_initial_intent_response(response, prompt)

    def patch_model(self, current_model: dict[str, Any], prompt: str, model: str) -> dict[str, Any]:
        system_prompt = (
            "You are a patch generator for a bridge engineering CAD tool. "
            "Return JSON only with keys patches and affected_views. "
            "Each patch must have op, path, value. "
            "Allowed paths are limited to the MVP bridge model surface, such as /bridge/spans_m, "
            "/bridge/spans_m/1, /bridge/deck_width_m, "
            "/bridge/superstructure/section_type, /bridge/superstructure/girder_depth_policy, "
            "/bridge/superstructure/girder_depth_m, /bridge/substructure/pier_type, "
            "/bridge/substructure/abutment_type, /bridge/alignment/start_station. "
            "affected_views may contain plan, elevation, typical_section."
        )
        user_prompt = (
            "Current model:\n"
            f"{json.dumps(current_model, ensure_ascii=True)}\n\n"
            "Edit request:\n"
            f"{prompt}"
        )
        response = self._generate_json(model, system_prompt, user_prompt)
        return _coerce_patch_response(response, current_model, prompt)

    def _generate_json(self, model: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\nUser request:\n{user_prompt}",
            "stream": False,
            "format": "json",
        }
        request = urllib.request.Request(
            url=f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach Ollama at {self.base_url}: {exc}") from exc

        raw_text = payload.get("response", "").strip()
        if not raw_text:
            raise RuntimeError("Ollama returned an empty response.")
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Ollama response was not valid JSON: {raw_text}") from exc


def _coerce_initial_intent_response(payload: dict[str, Any], prompt: str) -> dict[str, Any]:
    mock = MockIntentBackend().parse_initial_intent(prompt)
    intent = payload.get("intent", {}) if isinstance(payload, dict) else {}
    assumptions = payload.get("assumptions", []) if isinstance(payload, dict) else []
    questions = payload.get("questions", []) if isinstance(payload, dict) else []

    merged_intent = {
        **mock["intent"],
        **{k: v for k, v in intent.items() if v not in (None, "", [], {})},
    }

    if "superstructure" in intent and isinstance(intent["superstructure"], dict):
        merged_intent["superstructure"] = {
            **mock["intent"]["superstructure"],
            **{k: v for k, v in intent["superstructure"].items() if v not in (None, "", [], {})},
        }
    if "substructure" in intent and isinstance(intent["substructure"], dict):
        merged_intent["substructure"] = {
            **mock["intent"]["substructure"],
            **{k: v for k, v in intent["substructure"].items() if v not in (None, "", [], {})},
        }

    merged_intent["bridge_type"] = _coerce_enum(
        merged_intent.get("bridge_type"),
        {"continuous_girder"},
        mock["intent"]["bridge_type"],
    )
    merged_intent["material"] = _coerce_enum(
        merged_intent.get("material"),
        {"prestressed_concrete"},
        mock["intent"]["material"],
    )
    merged_intent["alignment_type"] = _coerce_enum(
        merged_intent.get("alignment_type"),
        {"straight", "curve"},
        mock["intent"]["alignment_type"],
    )
    merged_intent["start_station"] = _coerce_start_station(
        merged_intent.get("start_station"),
        mock["intent"]["start_station"],
    )
    merged_intent["requested_drawings"] = _coerce_requested_drawings(
        merged_intent.get("requested_drawings"),
        mock["intent"]["requested_drawings"],
    )
    merged_intent["superstructure"]["section_type"] = _coerce_enum(
        merged_intent["superstructure"].get("section_type"),
        {"single_box_single_cell", "single_box_double_cell"},
        mock["intent"]["superstructure"]["section_type"],
    )
    merged_intent["superstructure"]["girder_depth_policy"] = _coerce_enum(
        merged_intent["superstructure"].get("girder_depth_policy"),
        {"auto", "manual"},
        mock["intent"]["superstructure"]["girder_depth_policy"],
    )
    merged_intent["substructure"]["pier_type"] = _coerce_enum(
        merged_intent["substructure"].get("pier_type"),
        {"double_column", "solid_pier"},
        mock["intent"]["substructure"]["pier_type"],
    )
    merged_intent["substructure"]["abutment_type"] = _coerce_enum(
        merged_intent["substructure"].get("abutment_type"),
        {"gravity", "seat"},
        mock["intent"]["substructure"]["abutment_type"],
    )

    deduped_assumptions = _dedupe_strings([*mock["assumptions"], *assumptions, *merged_intent.get("assumptions", [])])
    deduped_questions = _dedupe_strings([*questions, *merged_intent.get("questions", [])])
    merged_intent["assumptions"] = deduped_assumptions
    merged_intent["questions"] = deduped_questions

    return {
        "intent": merged_intent,
        "assumptions": deduped_assumptions,
        "questions": deduped_questions,
    }


def _coerce_patch_response(payload: dict[str, Any], current_model: dict[str, Any], prompt: str) -> dict[str, Any]:
    mock = MockIntentBackend().patch_model(current_model, prompt)
    patches = payload.get("patches", []) if isinstance(payload, dict) else []
    affected_views = payload.get("affected_views", []) if isinstance(payload, dict) else []

    valid_patches = [patch for patch in patches if _is_valid_patch(patch)]
    if not valid_patches:
        valid_patches = mock["patches"]

    valid_views = sorted({view for view in affected_views if view in {"plan", "elevation", "typical_section"}})
    if not valid_views:
        valid_views = mock["affected_views"]

    return {
        "patches": valid_patches,
        "affected_views": valid_views,
    }


def _is_valid_patch(patch: Any) -> bool:
    return (
        isinstance(patch, dict)
        and patch.get("op") in {"replace", "add", "remove"}
        and isinstance(patch.get("path"), str)
        and patch["path"].startswith("/bridge/")
        and "value" in patch
    )


def _dedupe_strings(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _coerce_enum(value: Any, allowed: set[str], fallback: str) -> str:
    if isinstance(value, str) and value in allowed:
        return value
    return fallback


def _coerce_start_station(value: Any, fallback: str) -> str:
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized.startswith("K") and "+" in normalized:
            return normalized
    return fallback


def _coerce_requested_drawings(value: Any, fallback: list[str]) -> list[str]:
    allowed = {"general_arrangement", "plan", "elevation", "typical_section"}
    if not isinstance(value, list):
        return fallback
    normalized = [item for item in value if isinstance(item, str) and item in allowed]
    return normalized if normalized else fallback
