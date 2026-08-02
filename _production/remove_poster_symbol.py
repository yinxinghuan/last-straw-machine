#!/usr/bin/env python3
"""Use Aigram img2img to remove the final stray pseudo-trademark glyph."""

import json
import subprocess
from pathlib import Path

import generate_boss_slice as api

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "_production" / "poster-request.json"
OUT = ROOT / "_production" / "poster-generated.png"
TEMP = ROOT / "_production" / "poster-symbol-fixed.webp"
FIX_RECORD = ROOT / "_production" / "poster-symbol-fix-request.json"
PROMPT = (
    "Edit the supplied square poster while preserving the exact composition, people, colors, title lettering, lighting "
    "and every object. Remove only the tiny red circled pseudo-trademark glyph immediately to the right of the final W "
    "in LAST STRAW and replace that tiny area with perfectly matching plain cream background. The only visible typography "
    "after the edit must be the exact two-line title TODAY'S LAST STRAW. Also do not add any copyright, registered, trademark, "
    "warning, label, logo, watermark, letters or symbols anywhere. No other visual change."
)

if __name__ == "__main__":
    source_url = json.loads(RECORD.read_text())["response_url"]
    result_url = api.image(PROMPT, source_url)
    api.download(result_url, TEMP)
    subprocess.run(["sips", "-s", "format", "png", str(TEMP), "--out", str(OUT)], check=True)
    FIX_RECORD.write_text(json.dumps({"endpoint":api.IMAGE_API,"origin":"https://aigram.app","ref_url":source_url,"prompt":PROMPT,"response_url":result_url}, ensure_ascii=False, indent=2) + "\n")
    print(OUT)
