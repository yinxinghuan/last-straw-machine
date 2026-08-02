#!/usr/bin/env python3
"""Generate the formal Today's Last Straw poster through Aigram transit."""

import json
import os
import ssl
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_production" / "poster-generated.png"
RECORD = ROOT / "_production" / "poster-request.json"
API = "https://chat.aiwaves.tech/aigram/api/gen-image"
HEADERS = {"Content-Type":"application/json","Origin":"https://aigram.app","Referer":"https://aigram.app/","User-Agent":"Mozilla/5.0"}
SSL_CONTEXT = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
PROMPT = """
Square cinematic mobile game poster on a simple deep teal-to-black studio background. The upper quarter is one perfectly
clean solid cream field containing only this large bold condensed red title on two lines:
TODAY'S
LAST STRAW

There is absolutely nothing else in the cream field. Below it, one circular photographic token containing an expressive
freckled white Western woman around 30 with a short copper-red bob, mustard blazer and teal shirt falls dramatically through
an open field of bright yellow brass Plinko pins. Her face is clear, anxious and large. At the very bottom, three separate
small photoreal visual clues float directly on the dark background with no boxes, frames or captions: a stern silver-haired
male boss holding a cardboard box; a cluster of office phones lighting up around shocked coworkers; one plain coffee cup
tipping beside an empty cardboard box. Strong downward motion, premium commercial lighting, deep teal, ink black, cream,
red and yellow palette, instantly readable fate-versus-you conflict at 160px. The title is the sole typography in the entire
image. No subtitle, no labels, no numbers, no Chinese, no fake glyphs, no extra letters, no warning symbol, no signs, no
badges, no plaque, no interface screenshot, no watermark, no logo, no East Asian styling, not anime.
""".strip()


def generate():
    payload = json.dumps({"prompt": PROMPT}).encode()
    last = None
    for attempt, pause in enumerate((3, 8, 15), 1):
        try:
            request = urllib.request.Request(API, data=payload, method="POST", headers=HEADERS)
            with urllib.request.urlopen(request, timeout=360, context=SSL_CONTEXT) as response:
                body = json.loads(response.read())
            url = body.get("url")
            if not url:
                raise RuntimeError(body)
            RECORD.write_text(json.dumps({"endpoint":API,"origin":HEADERS["Origin"],"prompt":PROMPT,"response_url":url}, ensure_ascii=False, indent=2) + "\n")
            return url
        except Exception as error:
            last = error
            if attempt < 3:
                time.sleep(pause)
    raise last or RuntimeError("poster generation failed")


def download(url):
    request = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=120, context=SSL_CONTEXT) as response:
        data = response.read()
    suffix = os.path.splitext(url.split("?")[0])[1].lower()
    if suffix and suffix != ".png":
        temp = OUT.with_suffix(suffix); temp.write_bytes(data)
        subprocess.run(["sips", "-s", "format", "png", str(temp), "--out", str(OUT)], check=True)
        temp.unlink()
    else:
        OUT.write_bytes(data)


if __name__ == "__main__":
    ROOT.joinpath("_production").mkdir(parents=True, exist_ok=True)
    download(generate())
    print(OUT)
