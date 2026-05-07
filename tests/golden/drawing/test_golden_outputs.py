import json
import unittest
from pathlib import Path

from src.CadInstructions import create_cad_instruction_batch
from src.DrawingPlanner import create_drawing_plan


ROOT = Path(__file__).resolve().parents[3]
BRIDGE_MODEL_PATH = ROOT / "fixtures" / "bridge-models" / "canonical-bridge-model.json"
DRAWING_PLAN_PATH = ROOT / "fixtures" / "drawing-plans" / "canonical-general-arrangement.json"
CAD_INSTRUCTION_PATH = (
    ROOT / "fixtures" / "cad-instructions" / "canonical-general-arrangement.json"
)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class GoldenDrawingOutputTests(unittest.TestCase):
    maxDiff = None

    def test_drawing_plan_matches_canonical_fixture(self) -> None:
        bridge_model = load_json(BRIDGE_MODEL_PATH)
        expected = load_json(DRAWING_PLAN_PATH)

        actual = create_drawing_plan(bridge_model)

        self.assertEqual(actual, expected)

    def test_cad_instruction_batch_matches_canonical_fixture(self) -> None:
        bridge_model = load_json(BRIDGE_MODEL_PATH)
        drawing_plan = create_drawing_plan(bridge_model)
        expected = load_json(CAD_INSTRUCTION_PATH)

        actual = create_cad_instruction_batch(bridge_model, drawing_plan)

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
