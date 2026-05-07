from __future__ import annotations

import argparse
from pathlib import Path

from src.Preview.preview_service import build_preview_svg


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BRIDGE_MODEL = ROOT / "fixtures" / "bridge-models" / "canonical-bridge-model.json"
DEFAULT_OUTPUT = ROOT / "fixtures" / "cad-instructions" / "canonical-preview.svg"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a VibeDraw SVG preview.")
    parser.add_argument(
        "--bridge-model",
        default=str(DEFAULT_BRIDGE_MODEL),
        help="Path to a BridgeModel JSON fixture.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path for the generated SVG preview.",
    )
    args = parser.parse_args()

    svg = build_preview_svg(args.bridge_model)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    print(f"Preview written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
