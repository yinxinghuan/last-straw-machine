#!/usr/bin/env python3
"""Replace the unclear toupee gag with a readable self-caused box fall."""

from __future__ import annotations

import json
import time
from pathlib import Path

import generate_boss_slice as api

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "generated"
SOURCE = json.loads(Path(__file__).with_name("remaining_results_manifest.json").read_text())["coffee"]
MANIFEST = Path(__file__).with_name("coffee_v3_manifest.json")

END_PROMPT = (
    "Preserve the exact same MARA face, short copper-red bob, freckles, mustard blazer, teal shirt, same silver-haired white "
    "male boss, four coworkers, Western office, cardboard box, coffee tray and camera axis from the reference. Final frame of "
    "the same physical-comedy shot from a slightly lower camera tilt: the one and only boss is now seated safely on the carpeted "
    "floor at frame right after slipping on the small coffee puddle he caused, legs forward, navy suit rumpled, both empty hands "
    "raised in stunned embarrassment. His entire single body is continuous and clearly visible from head to shoes. The large plain "
    "cardboard box remains empty on the table above and behind him. Mara stands dry at frame left holding the empty tray and gives "
    "one restrained relieved smile. Exactly four coworkers remain seated in the background, covering their mouths. Exactly six "
    "human beings total: Mara, one boss, four coworkers. Broad but believable workplace visual comedy, clear cause and effect, "
    "premium live-action final shot. No person in the box, no detached limbs, no duplicate boss, no extra person, no injury, no "
    "toupee, no readable text, no cup brand, no logo, no watermark, no subtitle, not anime."
)

VIDEO_PROMPT = (
    "One continuous 10-second live-action workplace physical-comedy shot preserving the exact Mara face, copper bob, mustard blazer, "
    "same silver-haired boss, four coworkers, office and camera axis. Beat one: the boss steps backward into Mara's coffee tray while "
    "grandly gesturing, one cup spills onto his navy suit and makes a small puddle, and he immediately turns to unfairly point at Mara; "
    "she braces for public humiliation. Beat two: still pointing and not watching his own feet, he takes one backward step onto the small "
    "puddle, loses balance, and windmills his arms while the coworkers realize what is happening. Beat three: the one and only boss lands "
    "safely seated on the carpeted floor at frame right, legs forward and hands raised, while the cardboard box stays empty on the table; "
    "coworkers cover their mouths and Mara allows one restrained relieved smile. End exactly on the supplied final frame. Clear self-caused "
    "consequence, natural gravity, one continuous camera tilt down. Exactly six people total. No person in the box, no detached limbs, no "
    "duplicate boss, no cut, no morphing, no toupee, no injury, no readable text, no subtitle, no logo."
)


def save(data: dict) -> None:
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"start_url": SOURCE["start_url"], "start_prompt": SOURCE["start_prompt"]}
    start_url = manifest["start_url"]
    end_url = manifest.get("end_url")
    if not end_url:
        print("generating coffee v2 end", flush=True)
        end_url = api.image(END_PROMPT, start_url)
        manifest.update(end_url=end_url, end_prompt=END_PROMPT); save(manifest)
    api.download(end_url, OUT / "coffee_end.webp")
    video_url = manifest.get("video_url")
    if not video_url:
        print("submitting coffee v2 10-second result", flush=True)
        submitted = api.post(api.VIDEO_SUBMIT, {"query":"", "params": {
            "image_url":start_url, "end_image_url":end_url, "prompt":VIDEO_PROMPT, "env":"prod",
            "target_image_ratio":"9x16", "video_time":10,
        }}, timeout=300)
        task_id = submitted.get("task_id") or submitted.get("data", {}).get("task_id")
        if not task_id:
            raise RuntimeError(submitted)
        manifest.update(video_task_id=task_id, video_prompt=VIDEO_PROMPT, video_time=10); save(manifest)
        deadline = time.time() + 2400
        while time.time() < deadline:
            time.sleep(10)
            polled = api.post(api.VIDEO_POLL, {"query":"", "params":{"task_id":task_id}}, timeout=300)
            status = polled.get("status") or polled.get("data", {}).get("status")
            print(f"coffee v2 video status={status}", flush=True)
            if status == "success":
                video_url = polled.get("url") or polled.get("data", {}).get("url")
                if not video_url:
                    raise RuntimeError(polled)
                manifest["video_url"] = video_url; save(manifest); break
            if status == "failed":
                raise RuntimeError(polled)
        else:
            raise TimeoutError(task_id)
    api.download(video_url, OUT / "coffee_result.mp4")
    print(json.dumps({"end":end_url,"video":video_url,"video_time":10}), flush=True)


if __name__ == "__main__":
    main()
