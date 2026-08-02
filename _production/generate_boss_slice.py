#!/usr/bin/env python3
"""Generate the first 10-second Last Straw result through formal project APIs."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

IMAGE_API = "https://chat.aiwaves.tech/aigram/api/gen-image"
VIDEO_SUBMIT = "https://u545921-b746-8a491f44.westc.seetacloud.com:8443/video"
VIDEO_POLL = "https://u545921-b746-8a491f44.westc.seetacloud.com:8443/video_task"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "generated"
MANIFEST = Path(__file__).with_name("boss_slice_manifest.json")

START_PROMPT = (
    "Vertical live-action workplace drama-comedy film still inside a square image, contemporary Western advertising "
    "agency conference room, late afternoon. The fixed protagonist MARA is a white Western woman around 30 with a "
    "short copper-red bob, pale freckled face, expressive green eyes, mustard-yellow tailored blazer over a dark teal "
    "shirt and charcoal trousers. She stands centered, humiliated but holding herself together, both hands empty at "
    "her sides. An arrogant silver-haired white male boss in a navy suit stands frame right and points sharply at one "
    "plain open cardboard belongings box on the conference table. Four diverse Western coworkers sit behind the glass "
    "wall, watching with worried restrained expressions. Premium short-drama cinematography, strong emotional tension, "
    "natural skin, believable office light, medium-wide 28mm composition, faces and hands inside the central 70 percent. "
    "Exactly six people. The box is empty and blank. No text, no letters, no signage, no subtitle, no logo, no watermark, "
    "no UI, no phone screen, not East Asian styling, not anime, not illustration, not 3D render."
)

END_PROMPT = (
    "Preserve the exact same MARA face, short copper-red bob, freckles, mustard blazer, teal shirt, exact same silver-haired "
    "male boss, four coworkers, conference room, camera axis and live-action cinematography from the reference. Final frame "
    "of the same workplace reversal: Mara now sits upright in the large navy executive chair at the head of the table, calm "
    "and newly respected. A confident older Black female company owner in an elegant cream suit stands immediately beside "
    "Mara and places one plain brass office key into Mara's open palm. The former boss stands at frame right, stunned, holding "
    "the same plain cardboard belongings box against his chest. The four coworkers behind the glass are now standing and "
    "smiling with visible relief, one beginning a restrained clap. Strong but believable power reversal, premium short-drama "
    "final shot, natural faces and contact shadows, central 70 percent safe area. Exactly seven people. No crown, no confetti, "
    "no readable text, no letters, no signage, no subtitle, no logo, no watermark, no UI, no duplicate face, no costume change, "
    "not East Asian styling, not anime, not illustration."
)

VIDEO_PROMPT = (
    "One continuous 10-second live-action workplace short-drama shot preserving the exact Mara face, copper bob, mustard blazer, "
    "silver-haired boss, four coworkers, conference room and camera axis from the supplied frames. Three fast readable emotional "
    "beats. Beat one: the boss shoves the single empty cardboard box toward Mara and points toward the exit; Mara absorbs the public "
    "humiliation without melodramatic crying. Beat two: the older Black female owner enters decisively from frame left, stops the boss "
    "with one raised palm, removes his plain office key, and slides the executive chair toward Mara; coworkers stand as they realize "
    "the truth. Beat three: Mara sits in the chair, the owner places the brass key in her palm, and the stunned former boss slowly picks "
    "up the same cardboard box while one coworker begins a restrained clap. End exactly on the supplied final pose. Crisp cause and "
    "effect, satisfying power reversal, natural human motion, one continuous short camera push. No cut, no morphing, no extra person, "
    "no readable text, no subtitle, no logo, no crown, no confetti."
)


def post(url: str, payload: dict, *, origin: bool = False, timeout: int = 900) -> dict:
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    if origin:
        headers.update({"Origin": "https://aigram.app", "Referer": "https://aigram.app/"})
    request = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST", headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def image(prompt: str, ref_url: str | None = None) -> str:
    payload = {"prompt": prompt}
    if ref_url:
        payload["ref_url"] = ref_url
    for attempt, delay in enumerate((3, 8, 15), 1):
        try:
            result = post(IMAGE_API, payload, origin=True)
            if not result.get("url"):
                raise RuntimeError(result)
            return result["url"]
        except (urllib.error.HTTPError, TimeoutError) as error:
            if attempt == 3:
                raise
            print(f"image retry {attempt}: {error}; wait {delay}s", flush=True)
            time.sleep(delay)
    raise RuntimeError("image generation failed")


def download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=600) as response:
        target.write_bytes(response.read())


def save(data: dict) -> None:
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    start_url = manifest.get("start_url")
    if not start_url:
        print("generating boss start frame", flush=True)
        start_url = image(START_PROMPT)
        manifest.update(start_url=start_url, start_prompt=START_PROMPT)
        save(manifest)
    download(start_url, OUT / "boss_start.webp")

    end_url = manifest.get("end_url")
    if not end_url:
        time.sleep(3)
        print("generating boss reversal frame", flush=True)
        end_url = image(END_PROMPT, start_url)
        manifest.update(end_url=end_url, end_prompt=END_PROMPT)
        save(manifest)
    download(end_url, OUT / "boss_end.webp")

    video_url = manifest.get("video_url")
    if not video_url:
        print("submitting 10-second boss reversal", flush=True)
        submitted = post(VIDEO_SUBMIT, {"query": "", "params": {
            "image_url": start_url,
            "end_image_url": end_url,
            "prompt": VIDEO_PROMPT,
            "env": "prod",
            "target_image_ratio": "9x16",
            "video_time": 10,
        }}, timeout=300)
        task_id = submitted.get("task_id") or submitted.get("data", {}).get("task_id")
        if not task_id:
            raise RuntimeError(submitted)
        manifest.update(video_task_id=task_id, video_prompt=VIDEO_PROMPT, video_time=10)
        save(manifest)
        deadline = time.time() + 2400
        while time.time() < deadline:
            time.sleep(10)
            result = post(VIDEO_POLL, {"query": "", "params": {"task_id": task_id}}, timeout=300)
            status = result.get("status") or result.get("data", {}).get("status")
            print(f"video status={status}", flush=True)
            if status == "success":
                video_url = result.get("url") or result.get("data", {}).get("url")
                if not video_url:
                    raise RuntimeError(result)
                manifest["video_url"] = video_url
                save(manifest)
                break
            if status == "failed":
                raise RuntimeError(result)
        else:
            raise TimeoutError(task_id)
    download(video_url, OUT / "boss_result.mp4")
    print(json.dumps({"start": start_url, "end": end_url, "video": video_url, "video_time": 10}), flush=True)


if __name__ == "__main__":
    main()
