import unittest
from pathlib import Path

from src.Preview import build_preview_svg


ROOT = Path(__file__).resolve().parents[3]
BRIDGE_MODEL_PATH = ROOT / "fixtures" / "bridge-models" / "canonical-bridge-model.json"


class SvgPreviewTests(unittest.TestCase):
    def test_svg_contains_expected_shapes_and_labels(self) -> None:
        svg = build_preview_svg(BRIDGE_MODEL_PATH)

        self.assertIn("<svg", svg)
        self.assertIn("GENERAL ARRANGEMENT", svg)
        self.assertIn("<polyline", svg)
        self.assertIn("<text", svg)
        self.assertIn("40m", svg)
        self.assertIn("70m", svg)

    def test_svg_uses_preview_canvas_background(self) -> None:
        svg = build_preview_svg(BRIDGE_MODEL_PATH)

        self.assertIn('fill="#f8fafc"', svg)
        self.assertIn('aria-label="VibeDraw preview"', svg)


if __name__ == "__main__":
    unittest.main()

