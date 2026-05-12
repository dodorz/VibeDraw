import unittest

from src.LlmService.backends import MockIntentBackend
from src.LlmService.parsing import create_patch_response, parse_prompt_to_intent


class ParsingTests(unittest.TestCase):
    def test_parse_prompt_extracts_bridge_fields(self) -> None:
        intent = parse_prompt_to_intent(
            "画一座40+70+40米跨径、桥宽7.5米的预应力连续梁桥，采用单箱双室，实体墩，重力式桥台。"
        )
        self.assertEqual(intent["spans_m"], [40, 70, 40])
        self.assertEqual(intent["deck_width_m"], 7.5)
        self.assertEqual(intent["superstructure"]["section_type"], "single_box_double_cell")
        self.assertEqual(intent["substructure"]["pier_type"], "solid_pier")

    def test_patch_response_detects_middle_span_change(self) -> None:
        current_model = {
            "project_id": "bridge_001",
            "bridge": {
                "spans_m": [40, 70, 40],
                "deck_width_m": 7.5,
                "superstructure": {
                    "section_type": "single_box_single_cell",
                    "girder_depth_policy": "auto",
                },
                "substructure": {
                    "pier_type": "double_column",
                    "abutment_type": "gravity",
                },
            },
        }
        patch = create_patch_response(current_model, "把中跨改成75米。")
        self.assertEqual(
            patch["patches"],
            [{"op": "replace", "path": "/bridge/spans_m/1", "value": 75}],
        )
        self.assertEqual(patch["affected_views"], ["elevation", "plan", "typical_section"])

    def test_parse_prompt_detects_requested_drawings(self) -> None:
        intent = parse_prompt_to_intent("画一座40+70+40米跨径的桥，只生成断面图。")
        self.assertEqual(intent["requested_drawings"], ["general_arrangement", "typical_section"])

    def test_patch_response_can_switch_to_section_only(self) -> None:
        current_model = {
            "project_id": "bridge_001",
            "bridge": {
                "spans_m": [40, 70, 40],
                "deck_width_m": 7.5,
                "superstructure": {
                    "section_type": "single_box_single_cell",
                    "girder_depth_policy": "auto",
                },
                "substructure": {
                    "pier_type": "double_column",
                    "abutment_type": "gravity",
                },
                "drawings": ["general_arrangement", "plan", "elevation", "typical_section"],
            },
        }
        patch = create_patch_response(current_model, "改成只出断面图。")
        self.assertIn(
            {
                "op": "replace",
                "path": "/bridge/drawings",
                "value": ["general_arrangement", "typical_section"],
            },
            patch["patches"],
        )
        self.assertEqual(patch["affected_views"], ["elevation", "plan", "typical_section"])

    def test_mock_backend_returns_service_shape(self) -> None:
        payload = MockIntentBackend().parse_initial_intent(
            "Draw a prestressed continuous girder bridge with spans 30+50+30 m and deck width 9.5 m."
        )
        self.assertIn("intent", payload)
        self.assertIn("assumptions", payload)
        self.assertIn("questions", payload)
        self.assertEqual(payload["intent"]["requested_drawings"][0], "general_arrangement")


if __name__ == "__main__":
    unittest.main()
