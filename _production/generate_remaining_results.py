#!/usr/bin/env python3
"""Generate the reply-all and coffee-spill 10-second result films sequentially."""

from __future__ import annotations

import json
import time
from pathlib import Path

import generate_boss_slice as api

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "generated"
MANIFEST = Path(__file__).with_name("remaining_results_manifest.json")
BOSS = json.loads(Path(__file__).with_name("boss_slice_manifest.json").read_text())

RESULTS = {
    "reply": {
        "start": (
            "Preserve the exact same MARA identity from the reference: white Western woman around 30, short copper-red bob, "
            "freckled pale face, green eyes, mustard tailored blazer, dark teal shirt and charcoal trousers. New vertical live-action "
            "workplace short-drama shot in the same contemporary Western advertising agency open office. Mara sits at her desk at center "
            "and has just pressed send on a laptop; she covers her mouth with one hand in instant horror. Around her, four diverse Western "
            "coworkers simultaneously look down at their own softly glowing phones and then toward her. The same arrogant silver-haired white "
            "male boss in a navy suit stands behind a glass office wall holding a large presentation board with a distinctive simple red fox "
            "drawing and looks smug. On Mara's desk is an open paper sketchbook containing the exact same distinctive red fox drawing, visibly "
            "hand-drawn. One readable visual fact: her idea matches his board. Premium realistic cinematography, emotional social tension, central "
            "70 percent safe area. No readable words, no letters, no email UI, no logo, no watermark, no subtitle, not East Asian styling, not anime."
        ),
        "end": (
            "Preserve the exact same Mara face, copper bob, mustard blazer, same silver-haired male boss, coworkers, agency and camera axis from "
            "the reference. Final frame of the same reply-all reversal: Mara now stands composed beside her open sketchbook while four coworkers "
            "have rolled their chairs into a protective semicircle facing her and applaud with relieved, supportive expressions. Each coworker "
            "points between Mara's hand-drawn red fox sketch and the identical fox on the boss's large presentation board. The exposed boss stands "
            "alone behind the glass, shoulders dropped, lowering the stolen board so it partly covers his navy suit. A confident older Black female "
            "company owner in a cream suit stands beside Mara and hands Mara the presentation clicker. Clear social validation and power reversal, "
            "premium live-action final shot, natural skin and hands, central 70 percent. No readable words, no letters, no email UI, no logo, no "
            "watermark, no subtitle, no crown, no confetti, no duplicate face, not East Asian styling, not anime."
        ),
        "video": (
            "One continuous 10-second live-action workplace short-drama shot preserving the exact Mara face, copper bob, mustard blazer, same boss, "
            "coworkers, office and camera axis. Beat one: Mara taps send, freezes and covers her mouth; four coworkers' phones light up and they look "
            "from her to the boss. Beat two: one coworker notices the identical red fox in Mara's open sketchbook and on the boss's presentation board, "
            "then silently shows the others; their worry becomes recognition and they roll their chairs toward Mara. Beat three: the older Black female "
            "owner enters, takes the presentation clicker from the exposed boss, gives it to Mara, and the coworkers applaud while the boss lowers the "
            "stolen board. End exactly on the supplied final frame. Fast readable cause and effect, satisfying social validation, natural movement, one "
            "short camera push. No cut, no morphing, no extra people, no readable words or email UI, no subtitle, no logo."
        ),
    },
    "coffee": {
        "start": (
            "Preserve the exact same MARA identity from the reference: white Western woman around 30, short copper-red bob, freckles, green eyes, "
            "mustard tailored blazer, teal shirt and charcoal trousers. Vertical live-action workplace comedy shot at the same Western advertising "
            "agency morning meeting. Mara stands centered holding a small tray with exactly two plain paper coffee cups. The same arrogant silver-haired "
            "white male boss in a navy suit has backed into the tray while grandly gesturing and one cup is frozen mid-spill across the front of his suit. "
            "He angrily blames Mara and points at her although his backward step clearly caused it. Four diverse coworkers watch with tense sympathy. "
            "Premium realistic physical comedy, readable unfair accusation, medium-wide 28mm framing, central 70 percent safe area. No readable text, no "
            "letters, no brand on cups, no logo, no watermark, no subtitle, not East Asian styling, not anime, not illustration."
        ),
        "end": (
            "Preserve the exact same Mara face, copper bob, mustard blazer, same silver-haired boss, coworkers, office and camera axis. Final frame of "
            "the same coffee-spill workplace comedy: Mara stands dry and finally allows one small relieved smile while holding the now-empty tray. The "
            "boss's soaked silver toupee has slid off cleanly and landed upright inside the same plain cardboard belongings box on the table, while his "
            "real closely shaved head is visible; he stares at the toupee in stunned silence, no injury. The four coworkers cover their mouths trying and "
            "failing not to laugh, but nobody points cruelly. The spill has punctured his intimidating performance rather than harming him. Premium "
            "live-action visual punchline, believable wet fabric and hairpiece, natural faces, central 70 percent. No readable text, no letters, no logo, "
            "no watermark, no subtitle, no extra person, no duplicate face, not East Asian styling, not anime."
        ),
        "video": (
            "One continuous 10-second live-action workplace physical-comedy shot preserving the exact Mara face, copper bob, mustard blazer, same boss, "
            "four coworkers, office and camera axis. Beat one: the boss steps backward into Mara's coffee tray while gesturing, the cup spills over his "
            "navy suit, and he immediately turns and unfairly points at her; Mara braces for another public humiliation. Beat two: he wipes his wet silver "
            "hair with one hand and the soaked toupee slowly loosens while coworkers notice and struggle to keep straight faces. Beat three: the toupee "
            "slides off without injury and drops neatly into the plain cardboard box; the boss looks into the box in stunned silence, coworkers cover their "
            "mouths, and Mara gives one restrained relieved smile. End exactly on the supplied final pose. Crisp physical causality, not frantic slapstick, "
            "natural human motion, one short camera push. No cut, no morphing, no flying wig beyond the single drop, no readable text, no subtitle, no logo."
        ),
    },
}


def save(data: dict) -> None:
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def run_result(key: str, prompts: dict, manifest: dict) -> None:
    item = manifest.setdefault(key, {})
    start_url = item.get("start_url")
    if not start_url:
        print(f"generating {key} start", flush=True)
        start_url = api.image(prompts["start"], BOSS["start_url"])
        item.update(start_url=start_url, start_prompt=prompts["start"]); save(manifest)
    api.download(start_url, OUT / f"{key}_start.webp")

    end_url = item.get("end_url")
    if not end_url:
        time.sleep(3)
        print(f"generating {key} end", flush=True)
        end_url = api.image(prompts["end"], start_url)
        item.update(end_url=end_url, end_prompt=prompts["end"]); save(manifest)
    api.download(end_url, OUT / f"{key}_end.webp")

    video_url = item.get("video_url")
    if not video_url:
        print(f"submitting {key} 10-second result", flush=True)
        submitted = api.post(api.VIDEO_SUBMIT, {"query": "", "params": {
            "image_url": start_url, "end_image_url": end_url, "prompt": prompts["video"],
            "env": "prod", "target_image_ratio": "9x16", "video_time": 10,
        }}, timeout=300)
        task_id = submitted.get("task_id") or submitted.get("data", {}).get("task_id")
        if not task_id:
            raise RuntimeError(submitted)
        item.update(video_task_id=task_id, video_prompt=prompts["video"], video_time=10); save(manifest)
        deadline = time.time() + 2400
        while time.time() < deadline:
            time.sleep(10)
            polled = api.post(api.VIDEO_POLL, {"query": "", "params": {"task_id": task_id}}, timeout=300)
            status = polled.get("status") or polled.get("data", {}).get("status")
            print(f"{key} video status={status}", flush=True)
            if status == "success":
                video_url = polled.get("url") or polled.get("data", {}).get("url")
                if not video_url:
                    raise RuntimeError(polled)
                item["video_url"] = video_url; save(manifest); break
            if status == "failed":
                raise RuntimeError(polled)
        else:
            raise TimeoutError(task_id)
    api.download(video_url, OUT / f"{key}_result.mp4")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    for key, prompts in RESULTS.items():
        run_result(key, prompts, manifest)
    print(json.dumps({key: {"video": manifest[key]["video_url"], "video_time": 10} for key in RESULTS}), flush=True)


if __name__ == "__main__":
    main()
