#!/usr/bin/env python3
"""Small, dependency-free starter for TBD production records, not a video editor."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, label):
    require(isinstance(value, (int, float)) and not isinstance(value, bool),
            f"{label}: expected a number")
    try:
        result = Fraction(str(value))
    except (ValueError, OverflowError) as error:
        raise ValueError(f"{label}: expected a finite number") from error
    require(result >= 0, f"{label}: must be non-negative")
    return result


def integer(value, label):
    require(type(value) is int and value >= 0, f"{label}: expected a non-negative integer")
    return value


def index(items, label):
    require(isinstance(items, list), f"{label}: expected a list")
    result = {}
    for item in items:
        require(isinstance(item, dict), f"{label}: expected objects")
        key = item.get("id")
        require(isinstance(key, str) and key.strip(), f"{label}: missing id")
        require(key not in result, f"{label}: duplicate id {key}")
        result[key] = item
    return result


def ceil(value):
    return -(-value.numerator // value.denominator)


def validate(project):
    """Check shared timeline constraints; return derived final-frame captions.

    This cannot judge acoustic identity, spoken meaning, real media or approvals.
    Source coordinates are normalized decoded seconds, using a declared origin.
    The starter handles straight cuts at speed 1, without overlap or retiming.
    """
    require(isinstance(project, dict), "project: expected an object")
    require(type(project.get("schema_version")) is int and project["schema_version"] == 1,
            "schema_version must be 1")
    require(project.get("kind") in ("synthetic", "episode"), "kind: synthetic or episode")
    profile = project["profile"]
    fps = Fraction(integer(profile["fps_num"], "fps_num"),
                   integer(profile["fps_den"], "fps_den"))
    require(fps > 0, "fps must be positive")
    intro = integer(profile["intro_frames"], "intro_frames")
    require(profile["format"] in ("full", "short"), "format: full or short")
    require(profile["format"] != "short" or intro == 0, "short clips must have zero intro frames")
    for axis in ("width", "height"):
        require(integer(profile[axis], axis) > 0, f"{axis}: must be positive")
    sources = index(project["sources"], "sources")
    segments = index(project["segments"], "segments")
    captions = index(project["captions"], "captions")
    require(sources and segments, "sources and segments cannot be empty")
    for source_id, source in sources.items():
        require(number(source["duration_seconds"], source_id) > 0, "source duration must be positive")
        require(isinstance(source.get("clock_origin"), str) and source["clock_origin"].strip(),
                f"{source_id}: declare clock_origin")
        if project["kind"] == "episode":
            sha = source.get("sha256")
            require(isinstance(sha, str) and len(sha) == 64
                    and all(c in "0123456789abcdef" for c in sha),
                    f"{source_id}: record the real SHA-256 before validation")
            require(isinstance(source.get("path"), str) and source["path"].strip(),
                    f"{source_id}: record the local source path")
    cursor = 0
    for segment_id, segment in segments.items():
        require(segment["source_id"] in sources, f"{segment_id}: unknown source")
        start = number(segment["source_start_seconds"], segment_id)
        end = number(segment["source_end_seconds"], segment_id)
        require(start < end <= number(sources[segment["source_id"]]["duration_seconds"], segment_id),
                f"{segment_id}: source interval out of bounds")
        a = integer(segment["body_start_frame"], segment_id)
        b = integer(segment["body_end_frame"], segment_id)
        require(a == cursor and b > a, f"{segment_id}: body segments must be contiguous from frame 0")
        require(abs((end - start) * fps - (b - a)) <= 1,
                f"{segment_id}: duration mismatch; this starter does not support retiming")
        cursor = b
    derived = []
    closed_turns = set()
    turn_speakers = {}
    previous_turn = None
    previous_end = 0
    for caption_id, caption in captions.items():
        require(caption["segment_id"] in segments, f"{caption_id}: unknown segment")
        segment = segments[caption["segment_id"]]
        start = number(caption["source_start_seconds"], caption_id)
        end = number(caption["source_end_seconds"], caption_id)
        seg_start = number(segment["source_start_seconds"], caption_id)
        seg_end = number(segment["source_end_seconds"], caption_id)
        require(seg_start <= start < end <= seg_end,
                f"{caption_id}: must fit inside one retained segment; split at edit boundaries")
        turn = caption.get("turn_id")
        speaker = caption.get("speaker_id")
        require(isinstance(turn, str) and turn.strip(), f"{caption_id}: missing turn_id")
        require(speaker is None or (isinstance(speaker, str) and speaker.strip()),
                f"{caption_id}: speaker_id must be a string or null")
        if turn in turn_speakers:
            require(turn_speakers[turn] == speaker, f"{caption_id}: one turn cannot contain different speakers")
            require(speaker is not None, f"{caption_id}: uncertain speaker needs an independent turn")
        turn_speakers[turn] = speaker
        if turn != previous_turn:
            require(turn not in closed_turns, f"{caption_id}: a resumed speaker needs a new turn_id")
            if previous_turn is not None:
                closed_turns.add(previous_turn)
        previous_turn = turn
        text = caption.get("text")
        require(isinstance(text, str) and text.strip(), f"{caption_id}: missing text")
        require(text == text.strip() and "\r" not in text and "\n\n" not in text,
                f"{caption_id}: invalid subtitle whitespace")
        require(len(text.splitlines()) <= 2, f"{caption_id}: at most two display lines")
        require(not any(marker in text for marker in ("[待核]", "【待核】", "[待审核]", "【待审核】", "[unknown]")),
                f"{caption_id}: internal review markers belong in editorial_notes")
        # Quantize outward, then clip only to the owning edit interval.
        a = intro + segment["body_start_frame"] + int((start - seg_start) * fps)
        b = min(intro + segment["body_end_frame"],
                intro + segment["body_start_frame"] + ceil((end - seg_start) * fps))
        require(a < b, f"{caption_id}: empty quantized interval")
        require(a >= previous_end,
                f"{caption_id}: final-frame captions overlap or are out of order; review the boundary")
        previous_end = b
        derived.append({"id": caption_id, "start_frame": a, "end_frame": b,
                        "text": text, "speaker_id": speaker, "turn_id": turn})
    return {"body_frames": cursor, "final_frames": intro + cursor,
            "fps": fps, "captions": derived}


def timestamp(frame, fps):
    # Millisecond timestamps round to nearest; frame coordinates remain canonical.
    milliseconds = int(Fraction(frame * 1000, 1) / fps + Fraction(1, 2))
    seconds, ms = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def srt(result):
    return "\n".join(f"{n}\n{timestamp(c['start_frame'], result['fps'])} --> "
                     f"{timestamp(c['end_frame'], result['fps'])}\n{c['text']}\n"
                     for n, c in enumerate(result["captions"], 1))


def doctor():
    print(f"Python {sys.version.split()[0]} — starter requires Python >= 3.11")
    healthy = sys.version_info >= (3, 11)
    for name in ("ffmpeg", "ffprobe"):
        path = shutil.which(name)
        if not path:
            print(f"{name}: MISSING (needed for media work; JSON/SRT demo still works)")
            healthy = False
            continue
        check = subprocess.run([path, "-version"], capture_output=True, text=True, timeout=10)
        print((check.stdout or check.stderr).splitlines()[0])
        healthy = healthy and check.returncode == 0
    print("No software installed; optional ASR/rendering tools are listed in docs/dependencies.md.")
    return 0 if healthy else 1


def initialize(destination):
    # mkdir without exist_ok makes accidental reuse fail before any files are copied.
    destination.mkdir(parents=True, exist_ok=False)
    for name in ("sources", "analysis", "captions", "renders", "verification"):
        (destination / name).mkdir()
    shutil.copyfile(ROOT / "templates/episode.example.json", destination / "project.json")
    shutil.copyfile(ROOT / "templates/episode-brief.md", destination / "README.md")
    shutil.copyfile(ROOT / "templates/review-report.md", destination / "verification/review-report.md")
    print(f"Created {destination}; fill the brief and project.json with your own source records.")
    print("The empty template intentionally does not pass validate. No media was copied or generated.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="read-only Python/FFmpeg availability check")
    init = commands.add_parser("init", help="create a new local episode directory")
    init.add_argument("destination", type=Path)
    check = commands.add_parser("validate", help="validate declared timeline/caption data, not media")
    check.add_argument("project", type=Path)
    export = commands.add_parser("export-srt", help="derive SRT from the canonical caption data")
    export.add_argument("project", type=Path)
    export.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            return doctor()
        if args.command == "init":
            initialize(args.destination)
            return 0
        project = json.loads(args.project.read_text(encoding="utf-8"))
        result = validate(project)
        if args.command == "export-srt":
            # Refuse overwrites; version the output instead.
            with args.output.open("x", encoding="utf-8") as output:
                output.write(srt(result))
            print(f"Wrote {len(result['captions'])} captions to {args.output}")
        else:
            print(f"PASS: declared structure only — {result['final_frames']} final frames, "
                  f"{len(result['captions'])} captions")
        print("Not verified: source bytes, audio, pictures, speaker identity, transcription, human review or publishing.")
        return 0
    except (ValueError, OSError, KeyError, TypeError, ZeroDivisionError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
