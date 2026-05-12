import json
import unittest
from pathlib import Path

from src.CadInstructions import create_cad_instruction_batch
from src.DrawingPlanner import create_drawing_plan


ROOT = Path(__file__).resolve().parents[3]
BRIDGE_MODEL_PATH = ROOT / "fixtures" / "bridge-models" / "canonical-bridge-model.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class DrawingGeneratorTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.bridge_model = load_json(BRIDGE_MODEL_PATH)
        self.drawing_plan = create_drawing_plan(self.bridge_model)
        self.batch = create_cad_instruction_batch(self.bridge_model, self.drawing_plan)

    def test_pier_locations_follow_cumulative_spans_in_elevation(self) -> None:
        girder = next(
            instruction
            for instruction in self.batch["instructions"]
            if instruction["id"] == "elevation_girder_bottom"
        )
        self.assertEqual(girder["points"], [[0, 0], [40, 0], [110, 0], [150, 0]])

    def test_plan_view_deck_edges_use_half_width_offsets(self) -> None:
        outline = next(
            instruction
            for instruction in self.batch["instructions"]
            if instruction["id"] == "plan_deck_outline"
        )
        self.assertEqual(outline["points"][0], [0, -123.75])
        self.assertEqual(outline["points"][2], [150, -116.25])

    def test_typical_section_outline_is_closed_rectangle(self) -> None:
        section = next(
            instruction
            for instruction in self.batch["instructions"]
            if instruction["id"] == "typical_section_outline"
        )
        self.assertTrue(section["closed"])
        self.assertEqual(section["points"][0], [190, 0])
        self.assertEqual(section["points"][-1], [190, -2.5])

    def test_instruction_metadata_fields_are_present(self) -> None:
        for instruction in self.batch["instructions"]:
            self.assertIn("layer", instruction)
            self.assertIn("view_id", instruction)
            self.assertIn("source_component_id", instruction)

    def test_drawing_plan_respects_requested_drawings(self) -> None:
        section_only_model = json.loads(json.dumps(self.bridge_model))
        section_only_model["bridge"]["drawings"] = ["general_arrangement", "typical_section"]

        drawing_plan = create_drawing_plan(section_only_model)

        self.assertEqual(
            [view["view_id"] for view in drawing_plan["views"]],
            ["typical_section_main"],
        )

    def test_instruction_batch_respects_requested_drawings(self) -> None:
        section_only_model = json.loads(json.dumps(self.bridge_model))
        section_only_model["bridge"]["drawings"] = ["general_arrangement", "typical_section"]

        drawing_plan = create_drawing_plan(section_only_model)
        batch = create_cad_instruction_batch(section_only_model, drawing_plan)

        instruction_ids = {instruction["id"] for instruction in batch["instructions"]}
        self.assertIn("typical_section_outline", instruction_ids)
        self.assertIn("title_general_arrangement", instruction_ids)
        self.assertNotIn("elevation_girder_bottom", instruction_ids)
        self.assertNotIn("plan_deck_outline", instruction_ids)
        title = next(
            instruction
            for instruction in batch["instructions"]
            if instruction["id"] == "title_general_arrangement"
        )
        self.assertEqual(title["view_id"], "typical_section_main")


if __name__ == "__main__":
    unittest.main()
